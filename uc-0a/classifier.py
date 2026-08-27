"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

# ── Allowed taxonomy (README.md §Classification Schema) ────────────────────
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

ALLOWED_PRIORITIES = ["Urgent", "Standard", "Low"]

# Severity keywords that force priority → Urgent (case-insensitive)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ── Category keyword rules (checked top-down; first match wins) ────────────
# Each entry: (category, list-of-keyword-patterns, default_priority)
# More-specific categories come first so they aren't shadowed by broader ones.
CATEGORY_RULES = [
    ("Heritage Damage", [r"\bheritage\b", r"\bmonument\b", r"\bhistoric(?:al)?\b"], "Standard"),
    ("Heat Hazard",     [r"\bheat\b", r"\bheatwave\b", r"\bheatstroke\b", r"\bsunstroke\b"], "Standard"),
    ("Drain Blockage",  [r"\bdrain\b", r"\bmanhole\b", r"\bsewer\b", r"\bsewage\b", r"\bnala\b", r"\bnallah\b"], "Standard"),
    ("Flooding",        [r"\bflood\b", r"\bfloods\b", r"\bflooded\b", r"\bflooding\b", r"\bwaterlog\b", r"\bwaterlogged\b", r"\bsubmerge\b", r"\bstranded\b", r"\bknee.?deep\b"], "Standard"),
    ("Pothole",         [r"\bpothole\b", r"\bpotholes\b"], "Standard"),
    ("Road Damage",     [r"\broad\s+damage\b", r"\bcrack(?:ed|s)?\b", r"\bsinking\b", r"\bcaved?\s*in\b",
                         r"\bfootpath\b", r"\bpavement\b", r"\btiles?\s+broken\b", r"\bupturned\b",
                         r"\broad\s+surface\b", r"\basphalt\b"], "Standard"),
    ("Streetlight",     [r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blights?\s+out\b",
                         r"\bflickering\b", r"\bsparking\b", r"\bdark\s+at\s+night\b",
                         r"\bno\s+light\b"], "Standard"),
    ("Waste",           [r"\bgarbage\b", r"\brubbish\b", r"\bwaste\b", r"\btrash\b", r"\blitter\b",
                         r"\bdumped?\b", r"\boverflowing\b", r"\bbin\b", r"\bdead\s+animal\b",
                         r"\bsmell\b", r"\bstink\b", r"\brefuse\b", r"\bdebris\b"], "Low"),
    ("Noise",           [r"\bnoise\b", r"\bloud\b", r"\bmusic\b", r"\bhonking\b",
                         r"\bmidnight\b", r"\bdecibel\b", r"\bblaring\b"], "Low"),
]

# Output CSV columns
OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]


def _match_severity(text: str):
    """Return the list of severity keywords found in *text*."""
    found = []
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
            found.append(kw)
    return found


def _match_category(text: str):
    """Return (category, matched_keywords, default_priority) or None."""
    for category, patterns, default_pri in CATEGORY_RULES:
        matched = []
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                matched.append(m.group())
        if matched:
            return category, matched, default_pri
    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Rules (from agents.md / skills.md / README.md):
    - Category must be exactly one of the allowed taxonomy values.
    - Severity keywords force priority to Urgent.
    - Reason must be one sentence citing specific words from the description.
    - Genuinely ambiguous complaints → Other + NEEDS_REVIEW.
    - Never invent categories or sub-categories.
    """
    # ── Guard: missing / null / bad rows ───────────────────────────────────
    if not row or not isinstance(row, dict):
        return {
            "complaint_id": "",
            "category": "Other",
            "priority": "Standard",
            "reason": "Row is missing or invalid; no description available to classify.",
            "flag": "NEEDS_REVIEW",
        }

    complaint_id = str(row.get("complaint_id", "")).strip()
    description = str(row.get("description", "")).strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    # ── Severity check ─────────────────────────────────────────────────────
    severity_hits = _match_severity(description)
    is_urgent = len(severity_hits) > 0

    # ── Category matching ──────────────────────────────────────────────────
    cat_match = _match_category(description)

    if cat_match:
        category, matched_words, default_priority = cat_match
        priority = "Urgent" if is_urgent else default_priority
        keyword_cite = ", ".join(f'"{w}"' for w in matched_words)
        reason = f"Classified as {category} because the description mentions {keyword_cite}."
        flag = ""
    else:
        # Genuinely ambiguous — nothing matched
        category = "Other"
        priority = "Urgent" if is_urgent else "Standard"
        reason = "No clear category keywords found in the description; flagged for manual review."
        flag = "NEEDS_REVIEW"

    # If urgent due to severity, append the severity citation to the reason
    if is_urgent:
        sev_cite = ", ".join(f'"{s}"' for s in severity_hits)
        reason += f" Priority set to Urgent due to severity keyword(s): {sev_cite}."

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

    Hardened against:
    - Null / empty / malformed rows (skips gracefully, continues processing).
    - Missing columns (treated as empty strings).
    - Produces the output CSV even if some rows fail.
    """
    results = []

    # ── Read ───────────────────────────────────────────────────────────────
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # header = row 1
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as exc:
                # Don't crash — record the failure and keep going
                complaint_id = ""
                try:
                    complaint_id = str(row.get("complaint_id", "")).strip()
                except Exception:
                    pass
                results.append({
                    "complaint_id": complaint_id,
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error processing row {row_num}: {exc}",
                    "flag": "NEEDS_REVIEW",
                })

    # ── Write ──────────────────────────────────────────────────────────────
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
