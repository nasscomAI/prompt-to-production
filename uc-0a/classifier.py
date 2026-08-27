"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
Built using RICE enforcement rules from agents.md and skills.md.
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole":        ["pothole", "pot hole"],
    "Flooding":       ["flood", "flooded", "flooding", "waterlogged", "water logging"],
    "Streetlight":    ["streetlight", "street light", "light out", "lights out", "flickering", "lamp"],
    "Waste":          ["garbage", "waste", "rubbish", "litter", "dumped", "bins", "dead animal"],
    "Noise":          ["noise", "music", "loud", "sound", "midnight"],
    "Road Damage":    ["road", "cracked", "sinking", "surface", "footpath", "tiles", "broken", "manhole"],
    "Heritage Damage":["heritage", "monument", "historic"],
    "Heat Hazard":    ["heat", "temperature", "hot"],
    "Drain Blockage": ["drain", "blocked drain", "drainage"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    desc_lower = description.lower()

    # Determine priority — check severity keywords first
    priority = "Standard"
    triggered_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            triggered_keyword = kw
            break

    # Determine category — match keywords
    matched_categories = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(category)
                break

    # Assign category and flag
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Build reason sentence citing specific words from description
    if triggered_keyword:
        reason = (
            f"Classified as {category} with Urgent priority because description "
            f"contains severity keyword '{triggered_keyword}': \"{description[:80]}...\""
            if len(description) > 80 else
            f"Classified as {category} with Urgent priority because description "
            f"contains severity keyword '{triggered_keyword}': \"{description}\""
        )
    else:
        reason = (
            f"Classified as {category} based on complaint description: "
            f"\"{description[:80]}...\""
            if len(description) > 80 else
            f"Classified as {category} based on complaint description: \"{description}\""
        )

    return {
        "complaint_id": complaint_id,
        "category":     category,
        "priority":     priority,
        "reason":       reason,
        "flag":         flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    # Read input
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            original_fieldnames = reader.fieldnames or []
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}")
        return

    if not rows:
        print("ERROR: Input file is empty.")
        return

    print(f"Read {len(rows)} rows from {input_path}")

    # Classify each row
    results = []
    errors = 0
    for i, row in enumerate(rows):
        try:
            if not row.get("description", "").strip():
                result = {
                    "complaint_id": row.get("complaint_id", f"ROW_{i+1}"),
                    "category":     "Other",
                    "priority":     "Low",
                    "reason":       "No description provided",
                    "flag":         "NEEDS_REVIEW",
                }
            else:
                result = classify_complaint(row)
            results.append({**row, **result})
        except Exception as e:
            print(f"WARNING: Failed to classify row {i+1} ({row.get('complaint_id', '?')}): {e}")
            results.append({
                **row,
                "complaint_id": row.get("complaint_id", f"ROW_{i+1}"),
                "category":     "ERROR",
                "priority":     "Low",
                "reason":       f"Classification failed: {e}",
                "flag":         "NEEDS_REVIEW",
            })
            errors += 1

    # Write output
    output_fields = list(original_fieldnames) + ["category", "priority", "reason", "flag"]
    # Remove duplicates while preserving order
    seen = set()
    final_fields = []
    for f in output_fields:
        if f not in seen:
            seen.add(f)
            final_fields.append(f)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=final_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Results written to {output_path}")
        print(f"Total rows: {len(results)} | Errors: {errors}")
        print("\nClassification summary:")
        for r in results:
            print(f"  {r['complaint_id']:12} | {r['category']:16} | {r['priority']:8} | {r.get('flag','')}")
    except Exception as e:
        print(f"ERROR: Could not write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)