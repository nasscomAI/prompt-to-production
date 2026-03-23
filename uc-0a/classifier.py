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

input_file = "../data/city-test-files/test_hyderabad.csv"
output_file = "results_hyderabad.csv"

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ["category"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        row["category"] = classify(row["complaint"])
        writer.writerow(row)

print("Done ✅")
