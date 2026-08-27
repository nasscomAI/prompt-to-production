import csv

categories = {
    "Garbage": ["garbage", "waste", "trash", "overflow"],
    
    "Water": ["water", "leakage", "pipe", "drain", "flood", "flooded", "rain"],
    
    "Electricity": ["light", "power", "electricity", "current"],
    
    "Road": ["road", "pothole", "street", "traffic", "collapsed", "crater"]
}

def classify(text):
    if not text:
        return "Other"
        
    text = text.lower()
    for category, keywords in categories.items():
        for word in keywords:
            if word in text:
                return category
    return "Other"

input_file = "../data/city-test-files/test_hyderabad.csv"
output_file = "results_hyderabad.csv"

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    writer.writerow(["Complaint", "Category"])

    for row in reader:
        # safer column handling
        complaint = row.get("description") or row.get("complaint") or ""
        
        category = classify(complaint)
        writer.writerow([complaint, category])

print("Done! Output saved to results_hyderabad.csv")