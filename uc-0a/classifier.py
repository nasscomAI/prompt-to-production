"""
UC-0A — Complaint Classifier
Classifies civic complaints by category and severity using keyword + context rules.
Usage: python classifier.py --input data/city-test-files/test_pune.csv --output output_pune.csv
"""
import argparse
import csv
import re
import os

# ── Category rules ──────────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "sanitation": ["garbage","waste","drain","drainage","sewage","overflow","bins",
                   "market waste","flood","mosquito","health risk","smell"],
    "water":      ["water supply","no water","water leak","leakage","flooding",
                   "flood","stormwater","rain","underpass flood","monsoon","waterlog"],
    "roads":      ["pothole","road","surface","tarmac","asphalt","pavement","footpath",
                   "divider","lane","highway","crater","subsidence","cobble","tyre",
                   "blowout","collapsed","buckle","sinking"],
    "electricity":["power","electricity","street light","streetlight","wiring","sparking",
                   "substation","tripped","electrocution","light","outage","dark"],
}

# Explicit domain overrides when ambiguous
WATER_FLOOD_TRIGGERS = ["flooded","flooding","stormwater drain","blocked drain",
                        "drain blocked","rainwater","monsoon flood","waterlogging"]

# ── Severity rules ──────────────────────────────────────────────────────────
HIGH_TRIGGERS = [
    "injur","hospital","casualt","child","danger","hazard","safety",
    "fire","electrocution","electrocuted","risk","lives at risk","ambulance",
    "dengue","disease","gas leak","collapse","structural","death","fatal",
    "burns","burn on contact","swallowed","fell","trip","fracture","risk to",
]
MEDIUM_TRIGGERS = [
    "multiple","several","many","traders","residents","commuters","passengers",
    "visitors","all","entire","repeated","recurring","days","week","month",
    "morning rush","regularly","ongoing","long","duration","affecting",
]

def classify_category(text: str) -> str:
    t = text.lower()
    # Water/flooding takes priority over roads for drain/flood keywords
    for kw in WATER_FLOOD_TRIGGERS:
        if kw in t:
            return "water"
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"

def classify_severity(text: str) -> str:
    t = text.lower()
    for trigger in HIGH_TRIGGERS:
        if trigger in t:
            return "high"
    for trigger in MEDIUM_TRIGGERS:
        if trigger in t:
            return "medium"
    return "low"

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, severity
    """
    text = row.get("description", "")
    complaint_id = row.get("complaint_id", "")
    category = classify_category(text)
    severity = classify_severity(text)
    return {
        "complaint_id": complaint_id,
        "category": category,
        "severity": severity,
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles missing/null rows gracefully.
    """
    results = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("complaint_id", "").strip():
                continue  # skip blank rows
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "other",
                    "severity": "low",
                })

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "severity"])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
