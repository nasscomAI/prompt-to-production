import csv

def classify(text):
    text = text.lower()

    if "water" in text:
        return "Water Issue"
    elif "road" in text:
        return "Road Issue"
    elif "garbage" in text:
        return "Sanitation"
    else:
        return "Other"


with open("../data/city-test-files/test_pune.csv", "r") as file:
    reader = csv.DictReader(file)
    
    results = []
    
    for row in reader:
        text = row.get("Complaint_Text", "")   # ✅ FIXED
        category = classify(text)
        row["category"] = category
        results.append(row)

with open("results_pune.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Done!")