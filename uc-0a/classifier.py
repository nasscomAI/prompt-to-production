import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing",
            "flag": "NEEDS_REVIEW"
        }

    # CATEGORY RULES
    if any(word in description for word in ["drilling", "drill", "idling", "engine", "truck", "noise"]):
        category = "Noise"
    elif any(word in description for word in ["rainwater", "flood", "waterlogged", "submerged"]):
        category = "Flooding"
    elif "drain" in description or "sewage" in description:
        category = "Drain Blockage"
    elif "pothole" in description or "crater" in description:
        category = "Pothole"
    elif any(word in description for word in ["streetlight", "lamp", "dark", "no lights"]):
        category = "Streetlight"
    elif any(word in description for word in ["garbage", "waste", "trash"]):
        category = "Waste"
    elif any(word in description for word in ["cracked", "broken road", "road damage"]):
        category = "Road Damage"
    elif "heritage" in description:
        category = "Heritage Damage"
    elif "heat" in description:
        category = "Heat Hazard"
    else:
        category = "Other"

    # PRIORITY RULES
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

    if any(word in description for word in urgent_keywords):
        priority = "Urgent"
    else:
        priority = "Standard"

    # FLAG
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    reason = f"Classified as {category} based on description keywords."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception:
                result = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Error processing row",
                    "flag": "NEEDS_REVIEW"
                }

            writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
