import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital",
    "ambulance","fire","hazard","fell","collapse"
]

CATEGORIES = [
    "Pothole","Flooding","Streetlight","Waste","Noise",
    "Road Damage","Heritage Damage","Heat Hazard",
    "Drain Blockage","Other"
]

def classify_complaint(row: dict) -> dict:
    text = row.get("description","").lower()

    category = "Other"

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water logging" in text:
        category = "Flooding"
    elif "light" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text:
        category = "Noise"
    elif "road" in text or "crack" in text:
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    elif "drain" in text:
        category = "Drain Blockage"

    priority = "Standard"
    for word in SEVERITY_KEYWORDS:
        if word in text:
            priority = "Urgent"

    reason = f"Classified based on keywords present in description."

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    with open(input_path, newline='', encoding="utf-8") as infile, \
         open(output_path, "w", newline='', encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["complaint_id","category","priority","reason","flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                result = classify_complaint(row)
                writer.writerow(result)
            except Exception:
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Results generated")