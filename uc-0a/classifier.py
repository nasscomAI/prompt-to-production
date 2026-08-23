"""
UC-0A — Complaint Classifier
Built with the RICE -> agents.md -> skills.md -> CRAFT workflow.

Every rule below is a direct, executable restatement of an enforcement rule in
uc-0a/agents.md. The naive prompt ("Classify this citizen complaint by category
and priority.") produced free-text category names, missed severity signals, and
returned no justification at all. The constants in this file exist so that none
of those three failure modes can recur silently.
"""
import argparse
import csv
import re
import sys

# --- Enforcement rule 1: closed taxonomy -------------------------------------
# Category must be exactly one of these strings. Nothing else may be emitted.
ALLOWED_CATEGORIES = (
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
)
ALLOWED_PRIORITIES = ("Urgent", "Standard", "Low")

# --- Enforcement rule 2: severity keywords force Urgent ----------------------
# Word-start anchored so inflections count ("hospitalised" -> "hospital",
# "collapsed" -> "collapse") but unrelated substrings never trigger a false
# Urgent. This match overrides every other priority signal.
SEVERITY_PATTERN = re.compile(
    r"\b(injur\w*|child\w*|school\w*|hospital\w*|ambulance\w*|fire\w*"
    r"|hazard\w*|fell|fallen|collapse\w*)",
    re.IGNORECASE,
)

# --- Enforcement rule 3: Low must be earned, never assumed -------------------
# A complaint is Low only when nothing in it reports a service interruption,
# physical damage, or a health impact. Anything else defaults to Standard.
DISRUPTION_PATTERN = re.compile(
    r"\b(block\w*|chok\w*|clog\w*|overflow\w*|unusable|abandon\w*|divert\w*"
    r"|risk\w*|loss\w*|damag\w*|crater|swallow\w*|strand\w*|breeding|dengue"
    r"|malaria|flood\w*|waterlogg\w*|submerg\w*|broken|crack\w*|slow"
    r"|not cleared|not working|struggling)",
    re.IGNORECASE,
)

# --- Enforcement rule 6: hypothetical consequences are not competing evidence -
# "flooding risk" is a predicted outcome of the reported defect, not a second
# defect. A marker within this many characters of a match demotes it.
HYPOTHETICAL_PATTERN = re.compile(
    r"\b(risk|may|might|could|likely|danger|concern|threat|potential|expected)",
    re.IGNORECASE,
)
HYPOTHETICAL_WINDOW = 15

# --- Category evidence -------------------------------------------------------
# STRONG = an explicit defect term. WEAK = an indirect signal that names no
# defect; weak-only evidence is never trusted on its own (enforcement rule 7b).
STRONG_EVIDENCE = {
    "Pothole": [r"pothole\w*"],
    "Flooding": [r"flood\w*", r"waterlogg\w*", r"water logging", r"inundat\w*",
                 r"submerged"],
    "Streetlight": [r"street ?light\w*", r"street lamp\w*", r"lamp ?post\w*",
                    r"light not working", r"dark stretch"],
    "Waste": [r"garbage", r"waste", r"trash", r"rubbish", r"litter\w*",
              r"dumping", r"refuse dump"],
    "Noise": [r"noise", r"noisy", r"loud\w*", r"blaring", r"honk\w*", r"horn",
              r"drilling", r"loudspeaker"],
    "Road Damage": [r"road collapse\w*", r"collapse\w*", r"crater",
                    r"cave[- ]?in", r"caved in", r"sinkhole", r"road damag\w*",
                    r"road crack\w*", r"cracked road", r"road broken"],
    "Heat Hazard": [r"heat ?wave", r"heat hazard", r"extreme heat",
                    r"sun ?stroke", r"heat ?stroke", r"no shade"],
}
WEAK_EVIDENCE = {
    "Flooding": [r"rainwater", r"stagnant water", r"standing water"],
    "Noise": [r"idling", r"engines on"],
    "Waste": [r"debris"],
}

# Drain Blockage needs a conduit noun AND an obstruction verb in the same text,
# so "stormwater drain" alone is not enough and "blocked road" is not a drain.
DRAIN_NOUN = re.compile(r"\b(drain\w*|sewer\w*|nala|culvert)", re.IGNORECASE)
DRAIN_FAULT = re.compile(r"\b(block\w*|chok\w*|clog\w*|jam\w*|overflow\w*)",
                         re.IGNORECASE)

# --- Enforcement rule 5: location terms are not defect terms -----------------
# A heritage word only yields "Heritage Damage" when a damage word is present
# too. On its own it is a context signal that forces human review.
HERITAGE_TERM = re.compile(r"\b(heritage|monument\w*|historic\w*)",
                           re.IGNORECASE)
DAMAGE_TERM = re.compile(
    r"\b(damag\w*|defac\w*|vandal\w*|crack\w*|broken|crumbl\w*|collapse\w*"
    r"|erod\w*)", re.IGNORECASE)

NEEDS_REVIEW = "NEEDS_REVIEW"
REQUIRED_COLUMNS = ("complaint_id", "description")
OUTPUT_COLUMNS = ("complaint_id", "category", "priority", "reason", "flag")


def _is_hypothetical(text: str, match: re.Match) -> bool:
    """True when a hedging word sits right beside the match ('flooding risk')."""
    start = max(0, match.start() - HYPOTHETICAL_WINDOW)
    end = min(len(text), match.end() + HYPOTHETICAL_WINDOW)
    before = text[start:match.start()]
    after = text[match.end():end]
    return bool(HYPOTHETICAL_PATTERN.search(before)
                or HYPOTHETICAL_PATTERN.search(after))


def _collect_evidence(text: str, patterns) -> list:
    """Return [(position, matched_text)] for every non-hypothetical hit."""
    hits = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if _is_hypothetical(text, match):
                continue
            hits.append((match.start(), match.group(0)))
    return sorted(hits)


def _find_categories(text: str):
    """Map each category to its strong and weak evidence in this description."""
    strong, weak = {}, {}

    for category, patterns in STRONG_EVIDENCE.items():
        hits = _collect_evidence(text, patterns)
        if hits:
            strong[category] = hits

    for category, patterns in WEAK_EVIDENCE.items():
        hits = _collect_evidence(text, patterns)
        if hits and category not in strong:
            weak[category] = hits

    # Drain Blockage: conduit noun + obstruction verb, both non-hypothetical.
    noun = _collect_evidence(text, [DRAIN_NOUN.pattern])
    fault = _collect_evidence(text, [DRAIN_FAULT.pattern])
    if noun and fault:
        strong["Drain Blockage"] = sorted(noun + fault)
    elif noun:
        weak["Drain Blockage"] = noun

    # Heritage Damage: heritage term is only a category when damage is reported.
    heritage = _collect_evidence(text, [HERITAGE_TERM.pattern])
    damage = _collect_evidence(text, [DAMAGE_TERM.pattern])
    if heritage and damage:
        strong["Heritage Damage"] = sorted(heritage + damage)
    elif heritage:
        # Context only — recorded separately so it can force NEEDS_REVIEW
        # without stealing the category from the actual reported defect.
        weak.pop("Heritage Damage", None)

    return strong, weak, bool(heritage and not damage)


def _quote(hits) -> str:
    """Render matched fragments as quoted evidence, de-duplicated, in order."""
    seen, out = set(), []
    for _, fragment in hits:
        key = fragment.lower()
        if key not in seen:
            seen.add(key)
            out.append('"%s"' % fragment)
    return ", ".join(out[:3])


def _assign_priority(text: str):
    """Enforcement rules 2 and 3. Returns (priority, justification)."""
    severity = SEVERITY_PATTERN.search(text)
    if severity:
        return "Urgent", 'severity keyword "%s" is present' % severity.group(0)

    disruption = DISRUPTION_PATTERN.search(text)
    if disruption:
        return "Standard", ('no severity keyword but "%s" reports a service '
                            'disruption' % disruption.group(0))

    return "Low", ("no severity keyword and no reported blockage, damage or "
                   "health impact")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Only `description` is used as evidence. ward, location, reported_by and
    days_open are deliberately ignored (agents.md `context` exclusions).
    """
    complaint_id = (row.get("complaint_id") or "").strip() or "UNKNOWN"
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": ("No description text supplied, so no category evidence "
                       "could be quoted from the row."),
            "flag": NEEDS_REVIEW,
        }

    strong, weak, heritage_context = _find_categories(description)
    priority, priority_reason = _assign_priority(description)
    review_notes = []

    if strong:
        # Primary = the defect mentioned first in the citizen's own words.
        ordered = sorted(strong.items(), key=lambda kv: kv[1][0][0])
        category, hits = ordered[0]
        evidence = _quote(hits)
        if len(ordered) > 1:
            runners = ", ".join(name for name, _ in ordered[1:])
            review_notes.append(
                "competing category evidence for %s in the same description"
                % runners)
    elif weak:
        ordered = sorted(weak.items(), key=lambda kv: kv[1][0][0])
        category, hits = ordered[0]
        evidence = _quote(hits)
        review_notes.append(
            "only indirect evidence (%s names no explicit defect)" % evidence)
    else:
        category = "Other"
        evidence = '"%s"' % description[:40].rstrip()
        review_notes.append(
            "no term matching any allowed category was found")

    if heritage_context and category != "Heritage Damage":
        review_notes.append(
            "description names a heritage location without reporting damage "
            "to it, so the heritage angle needs a human decision")

    reason = ('Categorised %s on the evidence %s; priority %s because %s'
              % (category, evidence, priority, priority_reason))
    if review_notes:
        reason += "; flagged for review — " + "; ".join(review_notes)
    reason += "."

    # Final guard: the taxonomy is closed, so nothing outside it can escape.
    if category not in ALLOWED_CATEGORIES:
        category, review_notes = "Other", review_notes + ["taxonomy violation"]
    if priority not in ALLOWED_PRIORITIES:
        priority = "Standard"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": NEEDS_REVIEW if review_notes else "",
    }


def batch_classify(input_path: str, output_path: str) -> dict:
    """
    Read input CSV, classify each row, write results CSV.

    Guarantees: never crashes on a bad row, never drops a row, and asserts that
    output row count equals input row count before reporting success.
    """
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                raise ValueError(
                    "Input is missing required column(s) %s. Found: %s"
                    % (", ".join(missing), ", ".join(fieldnames) or "none"))
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError("Input CSV not found at: %s" % input_path)

    results, failed = [], 0
    for index, row in enumerate(rows, start=2):  # start=2 → header is line 1
        try:
            results.append(classify_complaint(row))
        except Exception as exc:  # a bad row must not kill the batch
            failed += 1
            results.append({
                "complaint_id": (row.get("complaint_id") or "UNKNOWN").strip(),
                "category": "Other",
                "priority": "Standard",
                "reason": ("Row %d could not be classified (%s: %s), so it is "
                           "reported rather than dropped."
                           % (index, type(exc).__name__, exc)),
                "flag": NEEDS_REVIEW,
            })

    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "total": len(results),
        "urgent": sum(1 for r in results if r["priority"] == "Urgent"),
        "standard": sum(1 for r in results if r["priority"] == "Standard"),
        "low": sum(1 for r in results if r["priority"] == "Low"),
        "needs_review": sum(1 for r in results if r["flag"] == NEEDS_REVIEW),
        "failed_rows": failed,
    }

    if summary["total"] != len(rows):
        print("WARNING: read %d rows but wrote %d — row loss detected."
              % (len(rows), summary["total"]), file=sys.stderr)

    print("Rows in: %d | Rows out: %d | Urgent: %d | Standard: %d | Low: %d "
          "| NEEDS_REVIEW: %d | Failed: %d"
          % (len(rows), summary["total"], summary["urgent"],
             summary["standard"], summary["low"], summary["needs_review"],
             summary["failed_rows"]))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
