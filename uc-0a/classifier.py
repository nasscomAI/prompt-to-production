import csv
import os

INPUT_FILE = "../data/city-test-files/test_hyderabad.csv"
OUTPUT_FILE = "results_hyderabad.csv"

URGENT_KEYWORDS = [
    "injury", "injured", "accident", "child", "school", "hospital",
    "fire", "flood", "electric shock", "dangerous", "emergency",
    "death", "fallen", "collapsed", "outbreak", "bleeding"
]

def assign_severity(text):
    text_lower = text.lower()
    for kw in URGENT_KEYWORDS:
        if kw in text_lower:
            return "URGENT"
    if any(w in text_lower for w in ["no water", "blocked", "major", "24 hours", "completely"]):
        return "HIGH"
    if any(w in text_lower for w in ["recurring", "again", "partial", "sometimes"]):
        return "MEDIUM"
    return "LOW"

def assign_category(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["road", "pothole", "footpath", "traffic", "street"]):
        return "Roads"
    if any(w in text_lower for w in ["water", "pipe", "supply", "leakage", "tap"]):
        return "Water Supply"
    if any(w in text_lower for w in ["garbage", "waste", "sanitation", "drain", "sewage", "smell"]):
        return "Sanitation"
    if any(w in text_lower for w in ["electricity", "power", "light", "electric", "wire", "streetlight"]):
        return "Electricity"
    if any(w in text_lower for w in ["safety", "crime", "theft", "police", "accident", "danger"]):
        return "Public Safety"
    if any(w in text_lower for w in ["hospital", "health", "disease", "outbreak", "mosquito"]):
        return "Health"
    if any(w in text_lower for w in ["park", "garden", "playground", "tree"]):
        return "Parks and Recreation"
    if any(w in text_lower for w in ["noise", "loud", "sound", "music", "horn"]):
        return "Noise Pollution"
    return "Other"

def get_department(category):
    mapping = {
        "Roads": "Roads & Infrastructure",
        "Water Supply": "Water Board",
        "Sanitation": "Sanitation Department",
        "Electricity": "TSSPDCL",
        "Public Safety": "Police / Safety",
        "Health": "Health Department",
        "Parks and Recreation": "Parks Department",
        "Noise Pollution": "Enforcement",
        "Other": "General Administration"
    }
    return mapping.get(category, "General Administration")

def classify_complaints(input_file, output_file):
    results = []
    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            complaint_id = row.get('complaint_id', '')
            complaint_text = row.get('complaint_text', '')
            category = assign_category(complaint_text)
            severity = assign_severity(complaint_text)
            department = get_department(category)
            results.append({
                'complaint_id': complaint_id,
                'complaint_text': complaint_text,
                'category': category,
                'severity': severity,
                'department': department
            })

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'complaint_id', 'complaint_text', 'category', 'severity', 'department'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done! {len(results)} complaints classified → {output_file}")

if __name__ == "__main__":
    classify_complaints(INPUT_FILE, OUTPUT_FILE)