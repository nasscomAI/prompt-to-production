"""
UC-0A — Complaint Classifier
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.

Enforcement rules implemented here (see agents.md / UC-0A spec):
  1. category must be EXACTLY one of the 10 allowed strings — no variations.
  2. priority is Urgent whenever a severity keyword is present in the description,
     regardless of category (severity overrides everything else).
  3. Every row's reason must quote the specific word(s) from the description that
     drove the category and/or priority decision.
  4. If category cannot be determined confidently from the description alone,
     category = "Other" and flag = "NEEDS_REVIEW". The classifier never guesses
     with false confidence on genuinely ambiguous input.

Design note on matching (important for generalizing beyond any one test file):
  Real complaint text uses many surface forms of the same concept — "flood",
  "flooded", "flooding", "floods". Hand-listing every inflection for every
  keyword is brittle: it only works for forms someone happened to think of.
  Instead, most terms below are matched as PREFIXES (e.g. root "flood" matches
  "flood", "flooded", "flooding", "floods", "floodwater", ...), which
  generalizes to inflections the test data never showed us.

  Prefix matching over-matches on some words ("hospital" would match
  "hospitality"), so every prefix root carries an explicit `exclude` list of
  known false-friend whole words that must NOT count as a match. Short,
  high-collision roots ("fire", "fell") are matched as exact whole words /
  a fixed list of irregular forms instead of prefixes, because the false-positive
  surface area of prefix-matching them (fireworks, fireplace, fellow...) is
  too large to safely exclude by name.
"""
import argparse
import csv
import re
import sys

# ---------------------------------------------------------------------------
# Schema constants (must match the table in the UC-0A spec exactly)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

PRIORITY_VALUES = ["Urgent", "Standard", "Low"]

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

# ---------------------------------------------------------------------------
# Severity terms (spec roots: injury, child, school, hospital, ambulance,
# fire, hazard, fell, collapse). Each root -> {"prefixes": [(root, exclude), ...],
# "exact": [literal whole-word/phrase forms not safe to prefix-match]}
# ---------------------------------------------------------------------------

SEVERITY_TERMS = {
    "injury":    {"prefixes": [("injur", [])], "exact": []},
    "child":     {"prefixes": [("child", [])], "exact": []},
    "school":    {"prefixes": [("school", [])], "exact": []},
    "hospital":  {"prefixes": [("hospital", ["hospitality", "hospitalities", "hospitable", "hospitably"])], "exact": []},
    "ambulance": {"prefixes": [("ambulance", [])], "exact": []},
    "hazard":    {"prefixes": [("hazard", [])], "exact": []},
    "collapse":  {"prefixes": [("collaps", [])], "exact": []},  # collapse/-d/-ing/-ible all start "collaps"
    # Short/high-collision roots: exact forms only, no prefix matching.
    "fire":      {"prefixes": [], "exact": ["fire", "fires", "fired", "on fire", "caught fire"]},
    "fell":      {"prefixes": [], "exact": ["fell", "fallen", "falling", "has fallen", "had fallen"]},
}

# Words/phrases immediately before a match that negate it ("no injuries",
# "not hospitalised") — these mean the severe outcome explicitly did NOT
# happen, so the keyword's presence should not force Urgent.
_NEGATION_PREFIX = r"\b(?:no|not|zero|without|any)\s+"

# ---------------------------------------------------------------------------
# Category terms. Order matters: first match wins when picking a single
# best-guess category, so more specific categories are listed before
# generic ones that could otherwise swallow them.
# ---------------------------------------------------------------------------

CATEGORY_TERMS = {
    "Heritage Damage": {
        "prefixes": [
            ("heritage", []),
            ("monument", ["monumental", "monumentally"]),
            ("archaeolog", []),
            ("historic", []),
        ],
        "phrases": ["old fort", "heritage site", "heritage zone", "heritage building"],
    },
    "Heat Hazard": {
        "prefixes": [
            ("heatwave", []),
            ("heatstroke", []),
            ("sunstroke", []),
        ],
        "phrases": ["heat wave", "extreme heat", "heat hazard"],
    },
    "Flooding": {
        "prefixes": [
            ("flood", []),
            ("waterlog", []),
            ("submerg", []),
        ],
        "phrases": ["water logging", "water-logging", "drain overflow", "water overflow", "flooding risk"],
    },
    "Drain Blockage": {
        "prefixes": [
            ("drain", []),
            ("sewer", []),
            ("sewage", []),
            ("stormwater", []),
            ("wastewater", []),
        ],
        "phrases": [],
    },
    "Pothole": {
        "prefixes": [
            ("pothole", []),
            ("crater", []),
        ],
        "phrases": ["pot hole", "pot holes", "hole in the road", "hole in road"],
    },
    "Road Damage": {
        "prefixes": [
            ("crumbl", []),
        ],
        "phrases": [
            "road damage", "cracked road", "broken road", "road broke",
            "road caved", "road collapse", "road collapsed", "damaged road",
        ],
    },
    "Streetlight": {
        "prefixes": [
            ("streetlight", []),
        ],
        "phrases": ["street light", "street lamp", "lamp post", "lamppost", "no light", "light not working"],
    },
    "Waste": {
        "prefixes": [
            ("garbage", []),
            ("rubbish", []),
            ("litter", []),
            ("trash", []),
            ("dump", []),
            ("waste", ["wasteful", "wastefully", "wastewater"],
             ["of money", "of time", "of resources", "of taxpayer", "of public money", "of public funds"]),
        ],
        "phrases": [],
    },
    "Noise": {
        "prefixes": [
            ("noise", ["noiseless"]),
            ("noisy", []),
            ("loud", []),
            ("honk", []),
            ("blar", []),
            ("disturb", []),
            ("drill", []),
            ("idl", []),  # idle/idled/idling
        ],
        "phrases": ["music at night", "engines running", "construction noise"],
    },
}

# Words/phrases that make an otherwise-matched category genuinely ambiguous
# because the description itself signals the writer isn't sure what it is.
AMBIGUITY_MARKERS = [
    "not sure", "unclear", "unknown issue", "something wrong",
    "can't tell", "cannot tell", "unsure",
]


def _prefix_matches(text_lower: str, root: str, exclude: list, not_followed_by: list = None) -> list:
    """
    All whole words in text_lower starting with `root`, minus excluded whole
    words, minus matches immediately followed by one of `not_followed_by`
    (used for idioms like "waste of money" that use the word but not the concept).
    """
    pattern = r"\b" + re.escape(root) + r"\w*"
    hits = []
    for m in re.finditer(pattern, text_lower):
        word = m.group()
        if word in exclude:
            continue
        if not_followed_by:
            tail = text_lower[m.end():m.end() + 20]
            if any(re.match(r"\s+" + re.escape(nf), tail) for nf in not_followed_by):
                continue
        hits.append(word)
    return hits


def _phrase_matches(text_lower: str, phrase: str) -> list:
    if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower):
        return [phrase]
    return []


def _term_matches(text_lower: str, term_spec: dict) -> list:
    """All surface-form hits for one term spec: dict with 'prefixes' and/or 'phrases'/'exact'."""
    hits = []
    for prefix_spec in term_spec.get("prefixes", []):
        root, exclude = prefix_spec[0], prefix_spec[1]
        not_followed_by = prefix_spec[2] if len(prefix_spec) > 2 else None
        hits.extend(_prefix_matches(text_lower, root, exclude, not_followed_by))
    for phrase in term_spec.get("phrases", []):
        hits.extend(_phrase_matches(text_lower, phrase))
    for exact in term_spec.get("exact", []):
        hits.extend(_phrase_matches(text_lower, exact))
    return hits


def _is_negated(text_lower: str, matched_word: str) -> bool:
    """True if `matched_word`'s first occurrence in text_lower is preceded by a negator."""
    idx = text_lower.find(matched_word)
    if idx == -1:
        return False
    preceding = text_lower[max(0, idx - 15):idx]
    return bool(re.search(_NEGATION_PREFIX + r"$", preceding))


def find_category_matches(description: str) -> dict:
    """Return {category: [matched surface forms]} for every category with >=1 hit."""
    lower = description.lower()
    matches = {}
    for category, spec in CATEGORY_TERMS.items():
        hits = _term_matches(lower, spec)
        if hits:
            matches[category] = sorted(set(hits))
    return matches


def find_severity_matches(description: str) -> list:
    """Return canonical severity roots present and not negated (e.g. ['school', 'hospital'])."""
    lower = description.lower()
    found = []
    for canonical, spec in SEVERITY_TERMS.items():
        hits = _term_matches(lower, spec)
        real_hits = [h for h in hits if not _is_negated(lower, h)]
        if real_hits:
            found.append(canonical)
    return found


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Expects `row` to contain at least a description-like field (tries, in order:
    'description', 'complaint', 'complaint_text', 'complaint_desc', 'issue_description',
    'text') and an id-like field (tries: 'complaint_id', 'id', 'ID', 'ticket_id').

    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = (
        row.get("complaint_id") or row.get("id") or row.get("ID")
        or row.get("ticket_id") or ""
    )

    description = (
        row.get("description")
        or row.get("complaint")
        or row.get("complaint_text")
        or row.get("complaint_desc")
        or row.get("issue_description")
        or row.get("text")
        or ""
    )
    description = (description or "").strip()

    # --- Rule 4: no usable description at all -> Other + NEEDS_REVIEW ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description text was provided to classify.",
            "flag": "NEEDS_REVIEW",
        }

    lower = description.lower()

    # --- Category detection ---
    category_matches = find_category_matches(description)
    ambiguity_hits = _term_matches(lower, {"phrases": AMBIGUITY_MARKERS})

    category = "Other"
    flag = ""
    category_reason_words = []

    if len(category_matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(category_matches) == 1:
        category, category_reason_words = next(iter(category_matches.items()))
        if ambiguity_hits:
            flag = "NEEDS_REVIEW"
    else:
        # More than one category plausible -> best-guess by declared priority
        # order, but never claim false confidence: always flag for review.
        for cat in CATEGORY_TERMS:
            if cat in category_matches:
                category = cat
                category_reason_words = category_matches[cat]
                break
        flag = "NEEDS_REVIEW"

    if category not in ALLOWED_CATEGORIES:
        # Defensive guard: enforcement rule 1 — never emit an out-of-schema value.
        category = "Other"
        flag = "NEEDS_REVIEW"

    # --- Priority detection (severity overrides category-based defaults) ---
    severity_hits = find_severity_matches(description)
    if severity_hits:
        priority = "Urgent"
    elif category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # --- Reason: must cite specific words from the description ---
    reason_parts = []
    if severity_hits:
        reason_parts.append(
            f"Marked Urgent due to severity keyword(s): {', '.join(sorted(set(severity_hits)))}."
        )
    if category_reason_words:
        reason_parts.append(
            f"Classified as {category} based on keyword(s): {', '.join(category_reason_words)}."
        )
    if flag == "NEEDS_REVIEW" and not category_reason_words:
        reason_parts.append(
            "No category keywords matched the description; category could not be confidently determined."
        )
    elif flag == "NEEDS_REVIEW" and len(category_matches) > 1:
        others = [c for c in category_matches if c != category]
        reason_parts.append(
            f"Description also matched other categories ({', '.join(others)}), so this needs human review."
        )
    elif flag == "NEEDS_REVIEW" and ambiguity_hits:
        reason_parts.append(
            f"Description contains uncertainty language ({', '.join(sorted(set(ambiguity_hits)))})."
        )

    reason = " ".join(reason_parts) if reason_parts else f"No specific keywords found; defaulted to {category}."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Never crashes on a bad row: any row that raises an exception during
    classification is still written to the output, with category=Other,
    priority=Standard, flag=NEEDS_REVIEW, and a reason explaining the failure.
    Produces output even if every row fails, and even if the input CSV has
    no rows at all (still writes a header-only output file).
    """
    rows_written = 0
    rows_failed = 0

    try:
        with open(input_path, newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                raise ValueError(f"Input file '{input_path}' has no header row / is empty.")

            with open(output_path, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
                writer.writeheader()

                for i, raw_row in enumerate(reader, start=1):
                    try:
                        if raw_row is None or all(
                            (v is None or str(v).strip() == "") for v in raw_row.values()
                        ):
                            result = {
                                "complaint_id": raw_row.get("complaint_id", "") if raw_row else "",
                                "category": "Other",
                                "priority": "Standard",
                                "reason": "Row was empty/null.",
                                "flag": "NEEDS_REVIEW",
                            }
                        else:
                            result = classify_complaint(raw_row)

                        # Final schema guard before writing.
                        if result.get("category") not in ALLOWED_CATEGORIES:
                            result["category"] = "Other"
                            result["flag"] = "NEEDS_REVIEW"
                        if result.get("priority") not in PRIORITY_VALUES:
                            result["priority"] = "Standard"

                        writer.writerow({k: result.get(k, "") for k in OUTPUT_FIELDS})
                        rows_written += 1

                    except Exception as exc:  # noqa: BLE001 - must not crash the batch
                        rows_failed += 1
                        fallback_id = ""
                        try:
                            fallback_id = raw_row.get("complaint_id", "") if raw_row else ""
                        except Exception:
                            pass
                        writer.writerow({
                            "complaint_id": fallback_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": f"Row {i} failed to classify due to an error: {exc}",
                            "flag": "NEEDS_REVIEW",
                        })
                        rows_written += 1

    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"ERROR: could not process input file '{input_path}': {exc}", file=sys.stderr)
        raise

    print(f"Rows written: {rows_written} (failed/flagged for review on error: {rows_failed})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")