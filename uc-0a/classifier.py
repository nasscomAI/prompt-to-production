import argparse
import csv
import os

def classify_complaint(row):
    description = row.get('description', '').lower()
    
    # Mapping synonyms to allowed categories
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flooding", "water logging", "waterlogging"],
        "Streetlight": ["streetlight", "lighting", "light"],
        "Waste": ["waste", "garbage", "trash", "dumping", "debris"],
        "Noise": ["noise", "loud"],
        "Road Damage": ["road damage", "road surface", "broken steps"],
        "Heritage Damage": ["heritage", "mandir", "temple"],
        "Heat Hazard": ["heat", "sun"],
        "Drain Blockage": ["drain", "sewer", "blockage"],
    }

    category = "Other"
    for official_cat, keywords in category_map.items():
        if any(word in description for word in keywords):
            category = official_cat
            break


    # 2. Enforcement: Priority Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Urgent" if any(word in description for word in urgent_keywords) else "Standard"

    # 3. Enforcement: Reason & Flag
    reason = f"Classification based on municipal keywords found in description."
    flag = "NEEDS_REVIEW" if category == "Other" else ""

    return {
        "complaint_id": row.get('complaint_id', 'N/A'),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(classify_complaint(row))
    
    keys = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"Success! Created {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)