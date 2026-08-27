import csv
import sys

def classify(complaint):
    c = complaint.lower()
    
    if any(w in c for w in ["pothole", "road damage", "road"]):
        category = "Pothole"
    elif any(w in c for w in ["flood", "waterlog", "flooding"]):
        category = "Flooding"
    elif any(w in c for w in ["streetlight", "street light", "light"]):
        category = "Streetlight"
    elif any(w in c for w in ["garbage", "waste", "trash"]):
        category = "Waste"
    elif any(w in c for w in ["noise", "sound"]):
        category = "Noise"
    elif any(w in c for w in ["drain", "drainage"]):
        category = "Drain Blockage"
    elif any(w in c for w in ["water pipe", "pipe burst"]):
        category = "Flooding"
    else:
        category = "Other"
    
    if any(w in c for w in ["child", "hospital", "school", "injury", "urgent"]):
        priority = "Urgent"
    elif any(w in c for w in ["broken", "not working", "burst"]):
        priority = "Standard"
    else:
        priority = "Low"
    
    return category, priority

rows = []
with open("../data/city-test-files/test_pune.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cat, pri = classify(row["complaint"])
        row["category"] = cat
        row["priority_flag"] = pri
        rows.append(row)

with open("results_pune.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Done!")
