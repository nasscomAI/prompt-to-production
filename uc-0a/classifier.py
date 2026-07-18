"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and ambiguity flag.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# Keyword patterns mapped to categories (checked in order)
CATEGORY_RULES = [
    ("Pothole",        [r"\bpothole\b"]),
    ("Flooding",       [r"\bflood", r"\bwaterlog", r"\bsubmerg", r"\bstrand"]),
    ("Streetlight",    [r"\bstreetlight\b", r"\bstreet\s*light\b", r"\blights?\s+out\b",
                        r"\bflicker", r"\blamp\s*post\b"]),
    ("Drain Blockage", [r"\bdrain\b", r"\bmanhole\b", r"\bsewer\b", r"\bblockage\b"]),
    ("Waste",          [r"\bgarbage\b", r"\bwaste\b", r"\bdump", r"\brefuse\b",
                        r"\btrash\b", r"\boverflowing\b", r"\bdead\s+animal\b",
                        r"\bnot\s+removed\b"]),
    ("Noise",          [r"\bnoise\b", r"\bloud\b", r"\bmusic\b", r"\bmidnight\b",
                        r"\bdecibel\b"]),
    ("Road Damage",    [r"\broad\s+(surface|crack|damag|sinking|broken)\b",
                        r"\bcrack(ed|s)?\b", r"\bsinking\b",
                        r"\bfootpath\b", r"\btile.*(broken|upturned)\b"]),
    ("Heritage Damage",[r"\bheritage\b", r"\bmonument\b", r"\bhistoric\b"]),
    ("Heat Hazard",    [r"\bheat\b", r"\bheatwave\b", r"\bsunstroke\b"]),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    # Handle empty/missing description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # --- Determine category ---
    matched_categories = []
    matched_evidence = []

    for cat, patterns in CATEGORY_RULES:
        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                matched_categories.append(cat)
                matched_evidence.append(match.group())
                break  # one match per category is enough

    if len(matched_categories) == 1:
        category = matched_categories[0]
        evidence_word = matched_evidence[0]
        flag = ""
    elif len(matched_categories) > 1:
        # Multiple categories matched — pick the first but flag as ambiguous
        category = matched_categories[0]
        evidence_word = matched_evidence[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        evidence_word = ""
        flag = "NEEDS_REVIEW"

    # --- Determine priority ---
    found_severity = [kw for kw in SEVERITY_KEYWORDS if re.search(r"\b" + kw + r"\b", desc_lower)]

    if found_severity:
        priority = "Urgent"
    elif any(term in desc_lower for term in ["risk", "danger", "serious", "stranded", "dark"]):
        priority = "Standard"
    else:
        priority = "Low"

    # --- Build reason ---
    if found_severity and evidence_word:
        reason = (
            f"Description mentions '{evidence_word}' indicating {category}, "
            f"and severity keyword '{found_severity[0]}' triggers Urgent priority."
        )
    elif found_severity:
        reason = (
            f"Severity keyword '{found_severity[0]}' found in description triggers Urgent priority; "
            f"category set to {category}."
        )
    elif evidence_word:
        reason = (
            f"Description mentions '{evidence_word}' indicating {category}."
        )
    else:
        reason = "No clear category keywords found in description; classified as Other."

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
    Handles bad rows without crashing; logs failures and continues.
    """
    results = []
    failed_rows = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                result = classify_complaint(row)
                # Preserve original columns and append classification fields
                out_row = dict(row)
                out_row["category"] = result["category"]
                out_row["priority"] = result["priority"]
                out_row["reason"] = result["reason"]
                out_row["flag"] = result["flag"]
                results.append(out_row)
            except Exception as e:
                print(f"Warning: row {i} failed classification ({e}), applying fallback.")
                out_row = dict(row)
                out_row["category"] = "Other"
                out_row["priority"] = "Low"
                out_row["reason"] = "Classification failed for this row."
                out_row["flag"] = "NEEDS_REVIEW"
                results.append(out_row)
                failed_rows.append(i)

    if not results:
        print("No rows to write.")
        return

    fieldnames = list(results[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} rows ({len(failed_rows)} fallback).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
