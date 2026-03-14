import csv

SEVERITY_KEYWORDS = [
    "injury","child","school","hospital","ambulance","fire","hazard","fell","collapse"
]

def classify_complaint(description):

    desc = description.lower()

    category = "Other"
    priority = "Standard"
    flag = ""

    if "pothole" in desc:
        category = "Pothole"

    elif "flood" in desc:
        category = "Flooding"

    elif "drain blocked" in desc or "stormwater drain" in desc or "main drain blocked" in desc:
        category = "Drain Blockage"

    elif "garbage" in desc or "waste" in desc:
        category = "Waste"

    elif "drilling" in desc or "noise" in desc or "engines" in desc:
        category = "Noise"

    elif "collapsed" in desc or "crater" in desc:
        category = "Road Damage"

    # priority check
    for word in SEVERITY_KEYWORDS:
        if word in desc:
            priority = "Urgent"

    reason = f'Classification based on description containing "{description.split()[0]}"'

    return category, priority, reason, flag


def batch_classify(input_file, output_file):

    with open(input_file, newline="") as infile, open(output_file, "w", newline="") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["category","priority","reason","flag"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:

            category, priority, reason, flag = classify_complaint(row["description"])

            row["category"] = category
            row["priority"] = priority
            row["reason"] = reason
            row["flag"] = flag

            writer.writerow(row)
