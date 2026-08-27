import csv

def classify(text):
    text = text.lower()
    
    if "garbage" in text or "waste" in text:
        return "Sanitation"
    elif "water" in text:
        return "Water"
    elif "road" in text:
        return "Infrastructure"
    else:
        return "Other"

input_file = "../data/city-test-files/test_pune.csv"
output_file = "results_pune.csv"

with open(input_file, "r") as file:
    reader = csv.reader(file)
    data = list(reader)

results = []

for row in data:
    if len(row) > 1:
        category = classify(row[1])
        results.append([row[0], row[1], category])

with open(output_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(results)

print("Done ✅ results_pune.csv created")