import csv

input_file = "../data/city-test-files/test_hyderabad.csv"
output_file = "results_hyderabad.csv"

rows = []

with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for row in reader:
        text = str(row).lower()

        if "garbage" in text:
            category = "sanitation"
        elif "water" in text:
            category = "water"
        elif "road" in text or "pothole" in text:
            category = "road"
        elif "electric" in text or "power" in text:
            category = "electricity"
        else:
            category = "other"

        row["category"] = category
        rows.append(row)

with open(output_file, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Results saved to", output_file)