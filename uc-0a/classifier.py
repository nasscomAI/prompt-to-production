import argparse
import csv

CATEGORY_KEYWORDS = {
    "Roads": ["pothole", "road", "footpath", "traffic", "signal", "pavement", "crater"],
    "Water": ["pipe", "leakage", "no water", "water supply", "tap", "drain"],
    "Sanitation": ["garbage", "waste", "drainage", "smell", "sewage", "dump"],
    "Electricity": ["power cut", "no electricity", "transformer", "wire", "outage", "blackout"],
}

CRITICAL_TRIGGERS = ["injury", "child", "school", "hospital", "accident", "emergency"]
HIGH_TRIGGERS = ["flooding", "flood", "no water for days", "fire", "collapse"]

def classify_complaint(row: dict) -> dict:
    text = row.get("complaint", row.get("text", "")).lower()

    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            category = cat
            break

    if any(t in text for t in CRITICAL_TRIGGERS):
        severity = "Critical"
        priority = 10
    elif any(t in text for t in HIGH_TRIGGERS):
        severity = "High"
        priority = 8
    elif len(text) > 100:
        severity = "Medium"
        priority = 5
    else:
        severity = "Low"
        priority = 3

    return {**row, "category": category, "severity": severity, "priority_score": priority}

def batch_classify(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = [classify_complaint(row) for row in rows]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Done! {len(results)} complaints classified → {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)