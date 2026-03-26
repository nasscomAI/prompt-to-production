import csv

def classify_complaint(text):
    text = text.lower()
    
    if "water" in text:
        return "Water"
    elif "road" in text:
        return "Road"
    elif "garbage" in text or "waste" in text:
        return "Garbage"
    elif "electricity" in text or "power" in text:
        return "Electricity"
    else:
        return "Other"

# Input and output file paths
input_file = "data/city-test-files/test_hyderabad.csv"
output_file = "uc-0a/results_hyderabad.csv"

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    
    # Add new column
    fieldnames = reader.fieldnames + ["Category"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        # Use correct column name
        category = classify_complaint(row["description"])
        row["Category"] = category
        writer.writerow(row)

print("Classification completed!")

# submission update