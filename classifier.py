import csv
import argparse

def classify_complaint(text):
    text = text.lower()

    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text:
        category = "Flooding"
    elif "streetlight" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    else:
        category = "Other"

    if any(word in text for word in ["injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"]):
        priority = "Urgent"
    else:
        priority = "Standard"

    reason = "Detected keywords in complaint description"

    return category, priority, reason, ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()

    with open(args.input) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for r in rows:
        category, priority, reason, flag = classify_complaint(r["description"])
        r["category"] = category
        r["priority"] = priority
        r["reason"] = reason
        r["flag"] = flag

    with open(args.output,"w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()
