import csv
import argparse

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description):
    text = description.lower()

    # CATEGORY (strict allowed list)
    if "pothole" in text:
        category = "Pothole"
    elif "flood" in text or "water" in text:
        category = "Flooding"
    elif "streetlight" in text or "dark" in text:
        category = "Streetlight"
    elif "garbage" in text or "waste" in text:
        category = "Waste"
    elif "noise" in text or "drilling" in text:
        category = "Noise"
    elif "drain" in text:
        category = "Drain Blockage"
    elif "road" in text and ("damage" in text or "collapsed" in text or "crater" in text):
        category = "Road Damage"
    elif "heritage" in text:
        category = "Heritage Damage"
    elif "heat" in text:
        category = "Heat Hazard"
    else:
        category = "Other"

    # PRIORITY
    if any(word in text for word in URGENT_KEYWORDS):
        priority = "Urgent"
    else:
        priority = "Standard"

    # REASON (must reference text)
    reason = f"Detected words in description related to {category}"
    
    # FLAG
    if category == "Other":
        flag = "NEEDS_REVIEW"
    else:
        flag = ""

    return category, priority, reason, flag


def batch_classify(input_file, output_file):
    results = []

    with open(input_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            desc = row["description"]

            category, priority, reason, flag = classify_complaint(desc)

            results.append([
                row.get("complaint_id", ""),
                desc,
                category,
                priority,
                reason,
                flag
            ])

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["complaint_id", "description", "category", "priority", "reason", "flag"])
        writer.writerows(results)

    print(f"Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    batch_classify(args.input, args.output)