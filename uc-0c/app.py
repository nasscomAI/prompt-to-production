# UC-0C: Number That Looks Right
# Robust version: works even if CSV headers have different capitalization or spaces
# Aggregates numbers per ward per category
# Output: growth_output.csv

import csv
from collections import defaultdict

# Function to read input CSV
def read_input(file_path):
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Normalize headers: strip spaces and lowercase
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
        data = []
        for row in reader:
            normalized_row = {k.strip().lower(): v for k, v in row.items()}
            data.append(normalized_row)
        return data

# Function to aggregate per ward per category
def aggregate_per_ward_category(data):
    agg = defaultdict(lambda: defaultdict(float))
    for row in data:
        ward = row.get("ward", "")
        category = row.get("category", "")
        try:
            value = float(row.get("value", 0))
        except ValueError:
            value = 0
        if ward and category:  # only aggregate valid rows
            agg[ward][category] += value
    return agg

# Function to save results
def save_results(agg, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ward", "category", "total"])
        for ward, categories in agg.items():
            for category, total in categories.items():
                writer.writerow([ward, category, total])

# Main execution
if __name__ == "__main__":
    # Replace with your file name if needed
    input_file = "../data/city-test-files/test_pune.csv"
    output_file = "growth_output.csv"

    data = read_input(input_file)
    agg = aggregate_per_ward_category(data)
    save_results(agg, output_file)

    print(f"UC-0C processing complete. Output saved to {output_file}")