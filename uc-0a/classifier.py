"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "") or ""
    desc_lower = description.lower()

    SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital",
                         "ambulance", "fire", "hazard", "fell", "collapse"]

    # --- Category detection: keyword signals per allowed category ---
    CATEGORY_SIGNALS = {
        "Pothole":         ["pothole"],
        "Flooding":        ["flood", "flooded", "knee-deep", "water"],
        "Streetlight":     ["streetlight", "street light", "lights out", "flickering"],
        "Waste":           ["garbage", "waste", "bin", "dumped", "dead animal"],
        "Noise":           ["music", "noise", "loud"],
        "Road Damage":     ["cracked", "sinking", "footpath", "tiles", "manhole"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard":     ["heat", "heatwave", "sunstroke"],
        "Drain Blockage":  ["drain blocked", "drain", "blocked"],
    }

    matched_categories = []
    matched_terms = []
    for category, keywords in CATEGORY_SIGNALS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                matched_terms.append(kw)
                break  # one match per category is enough

    # --- Priority detection ---
    severity_hits = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    priority = "Urgent" if severity_hits else "Standard"

    # --- Decide category + flag ---
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason = f"Classified as {category} due to mention of '{matched_terms[0]}'"
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Multiple possible categories matched ({', '.join(matched_categories)}); needs human review"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No category keywords matched in description; needs human review"

    if priority == "Urgent":
        reason += f"; marked Urgent due to '{severity_hits[0]}'"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    fieldnames = ["complaint_id", "date_raised", "city", "ward", "location",
                  "description", "reported_by", "days_open",
                  "category", "priority", "reason", "flag"]

    results = []
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classification = classify_complaint(row)
                merged = {**row, **classification}
                results.append(merged)
            except Exception as e:
                row["category"] = "Other"
                row["priority"] = "Standard"
                row["reason"] = f"Row failed to classify: {e}"
                row["flag"] = "NEEDS_REVIEW"
                results.append(row)

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
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