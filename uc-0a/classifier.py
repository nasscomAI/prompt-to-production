import argparse
import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance",
    "fire","hazard","fell","collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood","water logging","water"],
    "Streetlight": ["streetlight","light"],
    "Waste": ["garbage","waste","trash"],
    "Noise": ["noise","loud"],
    "Road Damage": ["road damage","crack","broken road"],
    "Heritage Damage": ["heritage","monument"],
    "Heat Hazard": ["heat"],
    "Drain Blockage": ["drain","sewer","blocked"]
}

def classify_complaint(row: dict) -> dict:
    description = row.get("description","").lower()

    category = "Other"
    flag = ""

    for cat, words in CATEGORY_KEYWORDS.items():
        if any(word in description for word in words):
            category = cat
            break

    if category == "Other":
        flag = "NEEDS_REVIEW"

    priority = "Standard"
    if any(word in description for word in SEVERITY_KEYWORDS):
        priority = "Urgent"

    reason = f"Detected keywords in description: {description[:40]}"

    return {
        "complaint_id": row.get("complaint_id",""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path, output_path):
    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_path,"w",newline='',encoding="utf-8") as outfile:
            fieldnames = ["complaint_id","category","priority","reason","flag"]
            writer = csv.DictWriter(outfile,fieldnames=fieldnames)

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)
                    writer.writerow(result)
                except Exception:
                    writer.writerow({
                        "complaint_id":row.get("complaint_id",""),
                        "category":"Other",
                        "priority":"Low",
                        "reason":"Processing error",
                        "flag":"NEEDS_REVIEW"
                    })