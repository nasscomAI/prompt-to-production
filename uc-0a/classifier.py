"""
UC-0A: Complaint Classifier
NASSCOM AI Code Sarathi — Prompt to Production
"""

import csv
import json
import sys
import os

# ── Category keyword map ──────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "Roads":       ["pothole", "road", "footpath", "pavement", "traffic",
                    "signal", "divider", "crater", "broken road"],
    "Water":       ["water", "pipe", "leak", "supply", "drainage",
                    "drain", "flood", "sewage overflow"],
    "Sanitation":  ["garbage", "waste", "sewage", "toilet", "sweeping",
                    "dustbin", "smell", "stench", "rubbish", "trash"],
    "Electricity": ["light", "electricity", "wire", "transformer",
                    "power", "streetlight", "electric", "outage"],
    "Parks":       ["park", "garden", "tree", "bench", "playground",
                    "grass", "hedge", "swing"],
}

# ── Severity keyword triggers (HIGH) ─────────────────────────────────────────
HIGH_KEYWORDS = [
    "injury", "injured", "accident", "child", "children",
    "school", "hospital", "fire", "danger", "dangerous",
    "emergency", "flood", "dead", "death", "bleeding", "fatal"
]

MEDIUM_KEYWORDS = [
    "many", "several", "multiple", "community", "area",
    "street", "public", "neighbourhood", "residents", "block", "colony"
]


def classify_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return "Other"


def classify_severity(text: str) -> str:
    text_lower = text.lower()
    for kw in HIGH_KEYWORDS:
        if kw in text_lower:
            return "High"
    for kw in MEDIUM_KEYWORDS:
        if kw in text_lower:
            return "Medium"
    return "Low"


def classify_complaint(text: str) -> dict:
    return {
        "category": classify_category(text),
        "severity": classify_severity(text),
    }


def run_on_csv(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        # Support both 'complaint_text' and 'complaint' column names
        text_col = None
        for col in ["complaint_text", "complaint", "description", "text"]:
            if col in fieldnames:
                text_col = col
                break

        if text_col is None:
            print(f"ERROR: No complaint text column found. Columns: {fieldnames}")
            sys.exit(1)

        for row in reader:
            text = row.get(text_col, "")
            result = classify_complaint(text)
            row["category"] = result["category"]
            row["severity"] = result["severity"]
            rows.append(row)

    out_fieldnames = list(fieldnames) + ["category", "severity"]
    # Remove duplicates if already present
    out_fieldnames = list(dict.fromkeys(out_fieldnames))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Classified {len(rows)} complaints → {output_path}")

    # Print summary
    categories = {}
    severities = {}
    for row in rows:
        categories[row["category"]] = categories.get(row["category"], 0) + 1
        severities[row["severity"]] = severities.get(row["severity"], 0) + 1

    print("\n📊 Category Breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat:<15} {count}")

    print("\n🚦 Severity Breakdown:")
    for sev in ["High", "Medium", "Low"]:
        print(f"   {sev:<10} {severities.get(sev, 0)}")


if __name__ == "__main__":
    # Usage: python classifier.py <city>
    # Example: python classifier.py pune
    if len(sys.argv) < 2:
        print("Usage: python classifier.py <city>")
        print("Example: python classifier.py pune")
        sys.exit(1)

    city = sys.argv[1].lower()
    input_file = f"../data/city-test-files/test_{city}.csv"
    output_file = f"results_{city}.csv"

    print(f"🏙️  Processing complaints for: {city.capitalize()}")
    run_on_csv(input_file, output_file)
   
