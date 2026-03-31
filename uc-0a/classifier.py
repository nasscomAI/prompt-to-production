import csv

def classify_complaint(text):
    text = text.lower()

    if "water" in text:
        return "Water"
    elif "road" in text or "pothole" in text:
        return "Road"
    elif "garbage" in text or "waste" in text:
        return "Garbage"
    elif "electricity" in text or "power" in text:
        return "Electricity"
    else:
        return "Other"


input_file = "../data/city-test-files/test_hyderabad.csv"
output_file = "results_hyderabad.csv"

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["Category"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        text = row.get("complaint", "")
        category = classify_complaint(text)

        row["Category"] = category
        writer.writerow(row)

print("Classification completed!")