"""
UC-0A — Complaint Classifier
Rule-based classifier built from agents.md and skills.md specifications.
"""
import argparse
import csv
import re
import sys

# ---------------------------------------------------------------------------
# Classification schema (from agents.md enforcement rules)
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword map — order matters: more specific categories checked first
# Each entry: (category_name, [keyword_patterns])
CATEGORY_KEYWORDS = [
    ("Heritage Damage", [
        r"heritage", r"monument", r"historical", r"ancient",
        r"archaeological", r"heritage\s+street",
    ]),
    ("Heat Hazard", [
        r"heat\s*wave", r"heatwave", r"sunstroke", r"heat\s+hazard",
        r"extreme\s+heat", r"heat\s+stroke",
    ]),
    ("Drain Blockage", [
        r"drain\s+block", r"blocked\s+drain", r"clogged\s+drain",
        r"manhole", r"sewer\s+block", r"nala\s+block", r"gutter\s+block",
        r"drain\s+overflow", r"drainage\s+block",
    ]),
    ("Streetlight", [
        r"streetlight", r"street\s+light", r"lamp\s*post",
        r"light\s+pole", r"lights?\s+out", r"bulb\s+out",
        r"lighting", r"flickering", r"sparking",
    ]),
    ("Flooding", [
        r"flood", r"waterlog", r"water\s*log", r"submerge",
        r"inundat", r"knee[\s-]*deep", r"waist[\s-]*deep",
        r"standing\s+in\s+water", r"water\s+stagnat",
    ]),
    ("Pothole", [
        r"pothole", r"pot\s*hole", r"pot[\s-]*hole",
    ]),
    ("Noise", [
        r"noise", r"noisy", r"loud", r"honking", r"blaring",
        r"music\s+past\s+midnight", r"sound\s+pollution",
        r"disturbance", r"playing\s+music",
    ]),
    ("Road Damage", [
        r"road\s+damage", r"road\s+surface\s+crack", r"crack",
        r"sinking", r"broken\s+road", r"asphalt", r"tar\s+damage",
        r"pavement\s+damage", r"road\s+repair", r"road\s+condition",
        r"footpath\s+.*broken", r"tiles?\s+broken", r"upturned",
    ]),
    ("Waste", [
        r"garbage", r"waste", r"trash", r"rubbish", r"litter",
        r"dump", r"debris", r"sanitation", r"overflowing\s+.*bin",
        r"dead\s+animal", r"not\s+removed",
    ]),
]


def _find_matching_words(text: str, patterns: list[str]) -> list[str]:
    """Return unique, non-overlapping words/phrases from text that matched."""
    matches: list[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            word = match.group(0)
            word_low = word.lower()
            # Skip if this match is a substring of an existing match
            if any(word_low in m.lower() for m in matches):
                continue
            # Remove existing matches that are substrings of this new one
            matches = [m for m in matches if m.lower() not in word_low]
            matches.append(word)
    return matches


def _detect_severity(description_lower: str) -> tuple[bool, list[str]]:
    """Check if any severity keywords are present. Returns (is_urgent, matched_keywords)."""
    found = []
    for kw in SEVERITY_KEYWORDS:
        # Use word boundary so "children" still matches "child", etc.
        if re.search(rf"\b{kw}", description_lower):
            found.append(kw)
    return (len(found) > 0, found)


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with at minimum complaint_id and description.
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement (from agents.md):
      - category must be one of the 10 allowed values
      - priority is Urgent when severity keywords are present, else Standard
      - reason cites specific words from the description
      - flag is NEEDS_REVIEW when category is ambiguous, else blank
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = (row.get("description") or "").strip()

    # --- Handle empty / unintelligible descriptions ---
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is missing or unintelligible.",
            "flag": "NEEDS_REVIEW",
        }

    description_lower = description.lower()

    # --- Determine priority from severity keywords ---
    is_urgent, severity_matches = _detect_severity(description_lower)
    priority = "Urgent" if is_urgent else "Standard"

    # --- Match categories ---
    matched_categories: list[tuple[str, list[str]]] = []
    for cat_name, patterns in CATEGORY_KEYWORDS:
        hits = _find_matching_words(description, patterns)
        if hits:
            matched_categories.append((cat_name, hits))

    # --- Decide category and flag ---
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        cited_words = _extract_salient_words(description)
        reason = (
            f"No clear category match; description mentions '{cited_words}'."
        )
    elif len(matched_categories) == 1:
        category = matched_categories[0][0]
        flag = ""
        cited_words = ", ".join(matched_categories[0][1])
        reason = _build_reason(category, priority, cited_words, severity_matches)
    else:
        # Multiple category matches — pick the first (highest-specificity)
        # but flag for review if the second match is a genuinely different category
        category = matched_categories[0][0]
        cited_words = ", ".join(matched_categories[0][1])

        secondary_cats = [c for c, _ in matched_categories[1:]]
        if any(c != category for c in secondary_cats):
            flag = "NEEDS_REVIEW"
            reason = (
                f"Classified as {category} based on '{cited_words}', "
                f"but description also matches {', '.join(secondary_cats)}."
            )
        else:
            flag = ""
            reason = _build_reason(category, priority, cited_words, severity_matches)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _build_reason(
    category: str,
    priority: str,
    cited_words: str,
    severity_matches: list[str],
) -> str:
    """Build a one-sentence reason citing specific words from the description."""
    base = f"Classified as {category} because description mentions '{cited_words}'"
    if severity_matches:
        base += f"; marked Urgent due to severity keyword(s): {', '.join(severity_matches)}"
    base += "."
    return base


def _extract_salient_words(description: str, max_words: int = 5) -> str:
    """Extract a few salient words from the description for the reason field."""
    words = re.findall(r"[a-zA-Z]{4,}", description)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for w in words:
        low = w.lower()
        if low not in seen:
            seen.add(low)
            unique.append(w)
    return ", ".join(unique[:max_words])


# ---------------------------------------------------------------------------
# Batch processing (from skills.md: batch_classify)
# ---------------------------------------------------------------------------

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Guarantees:
      - Never crashes partway — every row produces output.
      - Failed rows get category=Other, priority=Low, flag=NEEDS_REVIEW.
      - Output CSV is always written, even if some rows fail.
    """
    results: list[dict] = []
    errors: list[str] = []

    # --- Read and classify ---
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # header is row 1
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as exc:
                    cid = row.get("complaint_id", f"row-{row_num}")
                    errors.append(f"Row {row_num} ({cid}): {exc}")
                    results.append({
                        "complaint_id": cid,
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Row processing failed.",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error reading input file: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Write output ---
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(results)
    except Exception as exc:
        print(f"Error writing output file: {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Report ---
    if errors:
        print(f"Warning: {len(errors)} row(s) failed to classify:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)

    print(f"Classified {len(results)} complaint(s).")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
