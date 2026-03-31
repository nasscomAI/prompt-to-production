import csv
import sys
import os

# -----------------------------------------------
# CONFIGURATION — Rule-based classification
# -----------------------------------------------

# Categories and their keywords
CATEGORY_KEYWORDS = {
    "Roads": ["road", "pothole", "footpath", "traffic", "accident", "bridge", "pavement", "speed"],
    "Water Supply": ["water", "pipe", "leak", "tap", "supply", "drainage", "borewell", "sewage"],
    "Sanitation": ["garbage", "waste", "dustbin", "sweeping", "smell", "drain", "toilet", "swachh"],
    "Electricity": ["light", "streetlight", "power", "electric", "wire", "pole", "outage", "transformer"],
}

# High severity keywords
HIGH_SEVERITY_KEYWORDS = [
    "injury", "injured", "accident", "child", "children", "school",
    "hospital", "fire", "flood", "flooding", "dangerous", "emergency",
    "death", "collapse", "fell", "broken wire", "electrocution"
]

# Medium severity keywords
MEDIUM_SEVERITY_KEYWORDS = [
    "block", "blocked", "overflow", "days", "weeks", "many",
    "residents", "colony", "area", "multiple", "several"
]


def classify_category(complaint_text):
    """Figure out which category the complaint belongs to."""
    text = complaint_text.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "Other"


def classify_severity(complaint_text):
    """Figure out how severe/urgent the complaint is."""
    text = complaint_text.lower()

    # Check for HIGH severity first
    for keyword in HIGH_SEVERITY_KEYWORDS:
        if keyword in text:
            return "High"

    # Check for MEDIUM severity
    for keyword in MEDIUM_SEVERITY_KEYWORDS:
        if keyword in text:
            return "Medium"

    # Default to LOW
    return "Low"


def process_complaints(input_file):
    """Read the CSV file, classify each complaint, save results."""

    # Figure out output filename
    # e.g., test_hyderabad.csv → results_hyderabad.csv
    base = os.path.basename(input_file)
    city = base.replace("test_", "").replace(".csv", "")
    output_file = f"results_{city}.csv"

    results = []

    print(f"Reading complaints from: {input_file}")

    # Read input CSV
    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Try common column names for the complaint text
            complaint = (
                row.get("complaint") or
                row.get("Complaint") or
                row.get("complaint_text") or
                row.get("text") or
                row.get("description") or
                ""
            )

            category = classify_category(complaint)
            severity = classify_severity(complaint)

            results.append({
                "complaint": complaint,
                "category": category,
                "severity": severity
            })

    # Write output CSV
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["complaint", "category", "severity"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done! Results saved to: {output_file}")
    print(f"Total complaints processed: {len(results)}")

    # Show a preview
    print("\n--- Preview (first 5 results) ---")
    for r in results[:5]:
        print(f"  [{r['severity']:6}] {r['category']:15} | {r['complaint'][:60]}...")


# -----------------------------------------------
# MAIN — Run the program
# -----------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python classifier.py <path-to-csv>")
        print("Example: python classifier.py ../data/city-test-files/test_hyderabad.csv")
        sys.exit(1)

    input_csv = sys.argv[1]

    if not os.path.exists(input_csv):
        print(f"Error: File not found: {input_csv}")
        sys.exit(1)

    process_complaints(input_csv)
