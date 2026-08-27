"""
UC-0A — Complaint Classifier
Classifies citizen complaints into predefined categories and priority levels.

Built using the RICE framework defined in agents.md and skills from skills.md.
"""
import argparse
import csv
import re
import os
import sys

# ---------------------------------------------------------------------------
# Constants — derived from agents.md enforcement rules
# ---------------------------------------------------------------------------

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that MUST trigger Urgent priority (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Category keyword map: each entry is (category, keyword_patterns, weight)
# Patterns are matched case-insensitively against the description.
# Weight is used when multiple categories match to pick the strongest signal.
CATEGORY_RULES = [
    (
        "Pothole",
        [r"\bpothole[s]?\b", r"\bpot[\s-]?hole[s]?\b"],
    ),
    (
        "Flooding",
        [r"\bflood(?:ed|ing|s)?\b", r"\bwaterlog(?:ged|ging)?\b",
         r"\bsubmerge[d]?\b", r"\binundate[d]?\b", r"\bknee[\s-]?deep\b",
         r"\bwater[\s-]?stagnation\b", r"\bwater[\s-]?accumulation\b"],
    ),
    (
        "Streetlight",
        [r"\bstreetlight[s]?\b", r"\bstreet[\s-]?light[s]?\b",
         r"\blamp[\s-]?post[s]?\b", r"\blight[\s-]?pole[s]?\b",
         r"\blights?\s+out\b", r"\bflickering\b", r"\bdark\s+(at\s+night|street|area)\b",
         r"\bsparking\b"],
    ),
    (
        "Waste",
        [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b", r"\brubbish\b",
         r"\bdump(?:ed|ing)?\b", r"\blitter(?:ed|ing)?\b",
         r"\boverflowing\s+(?:garbage|bins?|dustbin)\b", r"\bdead\s+animal\b",
         r"\bsanitation\b", r"\bbulk\s+waste\b", r"\bdebris\b"],
    ),
    (
        "Noise",
        [r"\bnoise\b", r"\bloud\b", r"\bmusic\s+past\s+midnight\b",
         r"\bhonking\b", r"\bblaring\b", r"\bdecibel\b",
         r"\bnoise\s+pollution\b", r"\bmidnight\b", r"\bdisturbance\b"],
    ),
    (
        "Road Damage",
        [r"\broad\s+(?:surface\s+)?(?:crack(?:ed|s)?|damag(?:e|ed)|sinking|broken)\b",
         r"\bcrack(?:ed|s)?\s+(?:road|surface)\b", r"\bsinking\s+road\b",
         r"\basphalt\b", r"\btar\b", r"\bfootpath\s+(?:tiles?\s+)?broken\b",
         r"\btiles?\s+broken\b", r"\bupturned\b",
         r"\bmanhole\s+cover\s+missing\b", r"\bmanhole\b"],
    ),
    (
        "Heritage Damage",
        [r"\bheritage\b", r"\bmonument(?:al)?\b", r"\bhistorical\b",
         r"\bancient\b", r"\barchaeological\b", r"\btemple\s+wall\b",
         r"\bold\s+structure\b", r"\bheritage\s+street\b"],
    ),
    (
        "Heat Hazard",
        [r"\bheat(?:wave)?\b", r"\bhot\s+surface\b", r"\bsunstroke\b",
         r"\bburning\s+surface\b", r"\btemperature\s+ris(?:e|ing)\b",
         r"\bheat\s+hazard\b"],
    ),
    (
        "Drain Blockage",
        [r"\bdrain(?:age)?\s+block(?:ed|age)?\b", r"\bclogg(?:ed|ing)\s+drain\b",
         r"\bsewer\b", r"\bblocked?\s+drain\b", r"\bgutter\b",
         r"\bdrain\s+overflow\b", r"\bdrain(?:age)?\b"],
    ),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _match_categories(description: str) -> list[tuple[str, list[str]]]:
    """
    Return a list of (category, matched_keywords) tuples for all categories
    that have at least one keyword match in the description.
    """
    desc_lower = description.lower()
    matches = []
    for category, patterns in CATEGORY_RULES:
        matched_words = []
        for pattern in patterns:
            found = re.findall(pattern, desc_lower)
            matched_words.extend(found)
        if matched_words:
            matches.append((category, matched_words))
    return matches


def _determine_category(description: str) -> tuple[str, list[str], str]:
    """
    Determine the best category for the description.

    Returns:
        (category, evidence_words, flag)
        - category: one of ALLOWED_CATEGORIES
        - evidence_words: list of matched keywords from the description
        - flag: 'NEEDS_REVIEW' if ambiguous, else ''
    """
    matches = _match_categories(description)

    if not matches:
        return ("Other", [], "NEEDS_REVIEW")

    if len(matches) == 1:
        return (matches[0][0], matches[0][1], "")

    # Multiple categories matched — pick the one with the most keyword hits.
    matches.sort(key=lambda m: len(m[1]), reverse=True)
    best = matches[0]
    second = matches[1]

    # If the top two are close in confidence, flag as ambiguous
    if len(best[1]) == len(second[1]):
        return (best[0], best[1], "NEEDS_REVIEW")

    return (best[0], best[1], "")


def _check_severity(description: str) -> tuple[str, list[str]]:
    """
    Check whether any severity keywords are present.

    Returns:
        (priority, matched_severity_keywords)
    """
    desc_lower = description.lower()
    found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower):
            found.append(kw)

    if found:
        return ("Urgent", found)
    return ("Standard", [])


def _build_reason(category: str, priority: str,
                  cat_evidence: list[str], sev_evidence: list[str]) -> str:
    """
    Build a single-sentence reason citing specific words from the description.
    """
    cat_words = ", ".join(f"'{w}'" for w in dict.fromkeys(cat_evidence))
    if priority == "Urgent" and sev_evidence:
        sev_words = ", ".join(f"'{w}'" for w in dict.fromkeys(sev_evidence))
        return (
            f"Classified as {category} due to keywords {cat_words} "
            f"and marked Urgent because of severity indicator(s) {sev_words} "
            f"found in the description."
        )
    if cat_words:
        return (
            f"Classified as {category} based on keywords {cat_words} "
            f"found in the description."
        )
    return f"Classified as {category}; no specific category keywords matched."


# ---------------------------------------------------------------------------
# Skill: classify_complaint  (skills.md)
# ---------------------------------------------------------------------------

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Input:  dict with at minimum 'description'; optionally 'complaint_id'.
    Output: dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement rules from agents.md are applied:
      - Exact category names only
      - Severity keywords → Urgent
      - Reason cites words from description
      - Ambiguous / missing → Other + NEEDS_REVIEW
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", None)

    # Enforcement: null / empty description fallback
    if description is None or str(description).strip() == "":
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    description = str(description).strip()

    # Step 1 — Determine category
    category, cat_evidence, flag = _determine_category(description)

    # Step 2 — Determine priority via severity keywords
    priority, sev_evidence = _check_severity(description)

    # If no severity keywords, decide between Standard and Low based on
    # whether category was confidently matched.
    if priority != "Urgent":
        priority = "Standard" if category != "Other" else "Low"

    # Step 3 — Build reason sentence citing specific words
    reason = _build_reason(category, priority, cat_evidence, sev_evidence)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ---------------------------------------------------------------------------
# Skill: batch_classify  (skills.md)
# ---------------------------------------------------------------------------

OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    - Gracefully skips rows that cause unexpected errors.
    - Always produces output even if some rows fail.
    - Raises FileNotFoundError if input file is missing.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(
            f"Input file not found: '{input_path}'. "
            "Please provide a valid path to a complaint CSV file."
        )

    results = []
    errors = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as exc:
                cid = row.get("complaint_id", f"row_{row_num}")
                errors.append(cid)
                print(
                    f"WARNING: Skipped {cid} (row {row_num}): {exc}",
                    file=sys.stderr,
                )

    # Write output CSV — even if some rows failed
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total = len(results) + len(errors)
    print(f"Classified {len(results)}/{total} complaints successfully.")
    if errors:
        print(f"Skipped complaints: {', '.join(errors)}", file=sys.stderr)


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
