# UC-0A — Complaint Classifier

**Core failure modes:** Taxonomy drift · Severity blindness · Missing justification · Hallucinated sub-categories · False confidence on ambiguity

---

import csv

# Define keywords for categories
categories = {
    "Water": ["water", "leak", "pipeline"],
    "Electricity": ["power", "electric", "light"],
    "Road": ["road", "pothole", "traffic"],
    "Sanitation": ["garbage", "waste", "drain"]
}

# Severity keywords
high_keywords = ["accident", "injury", "fire", "hospital", "school"]
medium_keywords = ["delay", "issue", "problem"]

def classify_complaint(text):
    text = text.lower()

    # Category detection
    category = "Other"
    for key, words in categories.items():
        if any(word in text for word in words):
            category = key
            break

    # Severity detection
    severity = "Low"
    if any(word in text for word in high_keywords):
        severity = "High"
    elif any(word in text for word in medium_keywords):
        severity = "Medium"

    return category, severity


# Input & Output files
input_file = "../data/city-test-files/test_hyderabad.csv"
output_file = "results_hyderabad.csv"

with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_file, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["category", "severity"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        complaint = row["complaint"]
        category, severity = classify_complaint(complaint)

        row["category"] = category
        row["severity"] = severity

        writer.writerow(row)

print("Classification complete. Output saved to results_hyderabad.csv")
## Commit Formula
UC-0A Fix severity blindness: no urgency detection → added injury/fire/hospital keyword rules.
```
