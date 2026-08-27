"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]


def classify_complaint(row: dict) -> dict:
    text = row.get("description", "").lower()

    # --- CATEGORY CLASSIFICATION ---
    if any(word in text for word in ["pothole", "crack", "ditch"]):
        category = "Pothole"
    elif any(word in text for word in ["flood", "waterlogging", "water"]):
        category = "Flooding"
    elif any(word in text for word in ["light", "streetlight", "lamp"]):
        category = "Streetlight"
    elif any(word in text for word in ["garbage", "trash", "waste"]):
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road" in text:
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif any(word in text for word in ["drain", "sewage", "blockage"]):
        category = "Drain Blockage"
    else:
        category = "Other"

    # --- PRIORITY ---
    if any(word in text for word in SEVERITY_KEYWORDS):
        priority = "Urgent"
    elif any(word in text for word in ["minor", "small", "low"]):
        priority = "Low"
    else:
        priority = "Standard"

    # --- REASON (must cite words from text) ---
    words = text.split()
    snippet = " ".join(words[:6]) if words else "no description"

    reason = f"Classified as {category} based on words '{snippet}'"

    # --- FLAG ---
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as e:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error processing row: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                }

            results.append(result)

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")