"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import sys

CATEGORIES = [
    ("Pothole", ["pothole", "crater", "hole in road"]),
    ("Flooding", ["flood", "waterlogging", "waterlogged", "stagnant water", "submerged"]),
    ("Streetlight", ["streetlight", "street light", "street-light", "light not working", "no lighting"]),
    ("Waste", ["garbage", "waste", "trash", "litter", "dumping", "rubbish"]),
    ("Noise", ["noise", "loud", "honking", "blaring", "construction noise"]),
    ("Road Damage", ["road damage", "damaged road", "broken road", "cracked road", "uneven road", "rough road"]),
    ("Heritage Damage", ["heritage", "monument", "historical"]),
    ("Heat Hazard", ["extreme heat", "heat wave", "scorching", "heat hazard"]),
    ("Drain Blockage", ["drain", "drainage", "blocked drain", "clogged", "sewer"]),
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
MODERATE_KEYWORDS = ["damage", "broken", "blocked", "crack", "danger", "unsafe", "accident", "leak"]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", row.get("id", ""))
    description = row.get("description", "")

    if not description or not isinstance(description, str) or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    category = "Other"
    matched_kw = ""
    for cat, keywords in CATEGORIES:
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                matched_kw = kw
                break
        if category != "Other":
            break

    if any(kw in desc_lower for kw in URGENT_KEYWORDS):
        priority = "Urgent"
    elif any(kw in desc_lower for kw in MODERATE_KEYWORDS):
        priority = "Standard"
    else:
        priority = "Low"

    if matched_kw:
        reason = f"Complaint mentions '{matched_kw}' indicating a {category.lower()} issue."
    elif category == "Other":
        reason = "Description does not clearly match any known category."
    else:
        reason = f"Description indicates a {category.lower()} issue."

    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    try:
        with open(input_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                try:
                    result = classify_complaint(row)
                    rows.append(result)
                except Exception as e:
                    print(f"Error processing row {i}: {e}", file=sys.stderr)
                    rows.append({
                        "complaint_id": row.get("complaint_id", row.get("id", f"row_{i}")),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Processing error: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Processed {len(rows)} complaints. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
