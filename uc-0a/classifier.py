import argparse
import csv

# Allowed categories (STRICT)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]

# Severity keywords → Urgent
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").lower()

    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # --- CATEGORY CLASSIFICATION ---
    if "pothole" in description:
        category = "Pothole"
    elif "flood" in description or "waterlogging" in description:
        category = "Flooding"
    elif "streetlight" in description or "dark" in description:
        category = "Streetlight"
    elif "garbage" in description or "waste" in description or "trash" in description:
        category = "Waste"
    elif "noise" in description or "loud" in description:
        category = "Noise"
    elif "road" in description and ("broken" in description or "damage" in description):
        category = "Road Damage"
    elif "drain" in description and ("block" in description or "clog" in description):
        category = "Drain Blockage"
    elif "heat" in description or "hot" in description:
        category = "Heat Hazard"
    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # --- PRIORITY CLASSIFICATION ---
    if any(word in description for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif "minor" in description or "small" in description:
        priority = "Low"
    else:
        priority = "Standard"

    # --- REASON (must cite words from description) ---
    reason = f"Detected keywords in description: '{description[:50]}'"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    try:
        with open(input_path, newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # Handle bad row but continue
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error processing row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

    except FileNotFoundError:
        print(f"❌ Input file not found: {input_path}")
        return

    # Write output
    with open(output_path, "w", newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Done. Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")

    args = parser.parse_args()

    batch_classify(args.input, args.output)