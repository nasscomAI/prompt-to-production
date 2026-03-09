"""
UC-0A — Complaint Classifier
Author: Gaddam Siddharth | City: Hyderabad
CRAFT loop: classify civic complaints from CSV → results CSV
"""

import csv
import json
import os

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE  = os.path.join(os.path.dirname(__file__), "../data/city-test-files/test_hyderabad.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../data/city-test-files/results_hyderabad.csv")

# ── Category keyword map ──────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "Roads":       ["pothole", "road", "footpath", "pavement", "crack", "broken road", "divider", "speed breaker"],
    "Water":       ["water", "pipe", "leakage", "supply", "drainage", "sewage", "flood", "overflow"],
    "Sanitation":  ["garbage", "waste", "trash", "dustbin", "sweeping", "cleanliness", "dumping", "litter"],
    "Electricity": ["light", "power", "electricity", "streetlight", "wire", "pole", "transformer", "electric"],
}

# ── Severity keyword map ──────────────────────────────────────────────────────
SEVERITY_KEYWORDS = {
    "Critical": ["injury", "accident", "hospital", "child", "school", "death", "fire", "collapse", "electrocution", "bleeding"],
    "High":     ["no water", "blocked", "open wire", "flooding", "broken completely", "days", "week"],
    "Low":      ["minor", "small", "slight", "once", "aesthetic", "cosmetic"],
}


# ── Skills ────────────────────────────────────────────────────────────────────

def classify_complaint(complaint_text: str) -> dict:
    """Classify a single complaint text into category/subcategory/severity."""
    text_lower = complaint_text.lower()

    # Determine category
    category = "Other"
    subcategory = "General"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                category = cat
                subcategory = kw.title()
                break
        if category != "Other":
            break

    # Determine base severity
    severity = "Medium"
    reasoning = "Routine complaint, no strong severity signal"

    for kw in SEVERITY_KEYWORDS["Low"]:
        if kw in text_lower:
            severity = "Low"
            reasoning = f"Low-signal keyword '{kw}' found; minor issue"
            break

    for kw in SEVERITY_KEYWORDS["High"]:
        if kw in text_lower:
            severity = "High"
            reasoning = f"High-impact keyword '{kw}' found; significant disruption"
            break

    # Critical override — always wins
    for kw in SEVERITY_KEYWORDS["Critical"]:
        if kw in text_lower:
            severity = "Critical"
            reasoning = f"Critical keyword '{kw}' found; immediate risk to safety"
            break

    return {
        "category":   category,
        "subcategory": subcategory,
        "severity":   severity,
        "reasoning":  reasoning,
    }


def read_csv_complaints(filepath: str) -> list:
    """Read complaint CSV and return list of row dicts."""
    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_results_csv(filepath: str, results: list):
    """Write classified results to output CSV."""
    fieldnames = ["complaint_id", "ward", "complaint_text", "category", "subcategory", "severity", "reasoning"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Reading complaints from: {INPUT_FILE}")
    complaints = read_csv_complaints(INPUT_FILE)
    print(f"  → {len(complaints)} complaints loaded")

    results = []
    for row in complaints:
        complaint_text = row.get("complaint_text", row.get("complaint", ""))
        classification  = classify_complaint(complaint_text)
        results.append({
            "complaint_id": row.get("complaint_id", row.get("id", "")),
            "ward":         row.get("ward", ""),
            "complaint_text": complaint_text,
            **classification,
        })

    write_results_csv(OUTPUT_FILE, results)
    print(f"Results written to: {OUTPUT_FILE}")

    # Print summary
    from collections import Counter
    severities = Counter(r["severity"] for r in results)
    categories = Counter(r["category"] for r in results)
    print("\n── Severity Summary ──")
    for k, v in severities.most_common():
        print(f"  {k:10s}: {v}")
    print("\n── Category Summary ──")
    for k, v in categories.most_common():
        print(f"  {k:12s}: {v}")


if __name__ == "__main__":
    main()
