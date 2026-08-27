import argparse
import csv
import re

SEVERITY_KEYWORDS_PATTERN = re.compile(
    r"\b(injury|injuries|injured|child|children|school|hospital|hospitalised|hospitalized|ambulance|fire|hazard|fell|collapse|collapsed)\b",
    re.IGNORECASE
)

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

CATEGORY_PATTERNS = [
    ("Drain Blockage", re.compile(r"\bdrains?\b.*\b(block|blocked|blockage|clog|clogged)\b|\b(block|blocked|blockage|clog|clogged)\b.*\bdrains?\b", re.IGNORECASE)),
    ("Pothole", re.compile(r"\b(potholes?)\b", re.IGNORECASE)),
    ("Heat Hazard", re.compile(r"\b(melting|44°c|45°c|52°c|heatwave|burns|full sun|heat hazard)\b", re.IGNORECASE)),
    ("Streetlight", re.compile(r"\b(streetlights?|street light|lamp post|lights out|darkness|unlit)\b", re.IGNORECASE)),
    ("Waste", re.compile(r"\b(garbage|wastes?|trash|dead animal|bins|overflowing|dumped)\b", re.IGNORECASE)),
    ("Noise", re.compile(r"\b(music|band|drilling|amplifiers|noise|loud)\b", re.IGNORECASE)),
    ("Flooding", re.compile(r"\b(floods?|flooded|flooding|waterlogging|waterlogged|submerged)\b", re.IGNORECASE)),
    ("Heritage Damage", re.compile(r"\b(heritage|ancient|historic|monument)\b", re.IGNORECASE)),
    ("Road Damage", re.compile(r"\b(road|footpath|tarmac|crater|paving|bridge|tiles|crack|cracked|sink|sinking|subsid|subsidence|collapse|collapsed)\b", re.IGNORECASE)),
]


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules in agents.md.
    Returns dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip() if row.get("complaint_id") else ""
    description = row.get("description", "").strip() if row.get("description") else ""

    # Handle missing or null description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description field in complaint input.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # 1. Category Classification based on taxonomy rules
    category = "Other"
    flag = ""

    for cat_name, pattern in CATEGORY_PATTERNS:
        if pattern.search(desc_lower):
            category = cat_name
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Enforce allowed category string
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Priority Determination (Urgent vs Standard vs Low)
    if SEVERITY_KEYWORDS_PATTERN.search(desc_lower):
        priority = "Urgent"
    elif any(kw in desc_lower for kw in ["low priority", "minor", "cosmetic"]):
        priority = "Low"
    else:
        priority = "Standard"

    # 3. Reason Generation (One sentence citing words from description)
    first_sentence = description.split('.')[0].strip()
    if not first_sentence.endswith('.'):
        first_sentence += '.'
    reason = f"Citing description: \"{first_sentence}\""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Flags nulls/bad rows, does not crash on bad input.
    """
    results = []

    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                except Exception as e:
                    # Robust crash-resilient error handling per skills.md
                    complaint_id = row.get("complaint_id", "UNKNOWN") if isinstance(row, dict) else "UNKNOWN"
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as err:
        print(f"Error reading input file {input_path}: {err}")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")


