import csv

def classify_complaint(text):
    text = text.lower()

    if "water" in text:
        return "Water Issue"
    elif "road" in text or "pothole" in text:
        return "Road Issue"
    elif "garbage" in text or "waste" in text:
        return "Sanitation Issue"
    elif "electricity" in text or "power" in text:
        return "Electricity Issue"
    else:
        return "Unclassified"


def main():
    input_file = "../data/complaints.csv"
    output_file = "results_nellore.csv"

    with open(input_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    for row in rows:
        row["category"] = classify_complaint(row["complaint"])

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(rows)

    print("Classification completed!")


if __name__ == "__main__":
    main()