import csv

def classify_complaint(text):
    text = text.lower()

    # Critical priority
    if "injury" in text or "hospital" in text or "school" in text:
        return "High Priority"

    # Category detection
    elif "water" in text:
        return "Water Issue"
    elif "road" in text:
        return "Road Issue"
    elif "garbage" in text:
        return "Sanitation Issue"
    else:
        return "Other"

input_file = "../data/city-test-files/test_pune.csv"
output_file = "results_pune.csv"

with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header + ["Category"])

    for row in reader:
        complaint = row[0]
        category = classify_complaint(complaint)
        writer.writerow(row + [category])

print("Classification completed. Check results_pune.csv")