import csv
import argparse
import os

def classify_complaint(description):
    desc_lower = str(description).lower()
    categories = ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]
    keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    category = "Other"
    for cat in categories:
        if cat.lower() in desc_lower:
            category = cat
            break
            
    priority = "Urgent" if any(word in desc_lower for word in keywords) else "Standard"
    reason = f"Classification based on keywords in description."
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    return category, priority, reason, flag

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path): return
    results = []
    with open(input_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get('description', row.get('desc', ''))
            cat, prio, reas, flg = classify_complaint(text)
            row.update({'category': cat, 'priority': prio, 'reason': reas, 'flag': flg})
            results.append(row)
    if results:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
