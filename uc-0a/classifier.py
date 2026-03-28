import csv
import sys
import os


# =========================
# Logic Layer
# =========================
def classify_category(text: str) -> str:
    """Classify complaint into category."""
    text = text.lower()

    if any(word in text for word in ["garbage", "waste", "drain"]):
        return "sanitation"
    if any(word in text for word in ["water", "leak", "pipeline"]):
        return "water"
    if any(word in text for word in ["power", "electricity", "wire"]):
        return "electricity"
    if any(word in text for word in ["road", "pothole", "construction"]):
        return "road"

    return "other"


def classify_severity(text: str) -> str:
    """Classify complaint severity."""
    text = text.lower()

    if any(word in text for word in ["injury", "hospital", "child", "accident"]):
        return "high"
    if any(word in text for word in ["many", "frequent", "recurring"]):
        return "medium"

    return "low"


def process_file(input_file: str, output_file: str):
    """Read input CSV, classify data, and write output CSV."""
    with open(input_file, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Add new columns
        fieldnames = reader.fieldnames + ["category", "severity"]

        with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                complaint = row.get("complaint", "")

                category = classify_category(complaint)
                severity = classify_severity(complaint)

                row["category"] = category
                row["severity"] = severity

                writer.writerow(row)


# =========================
# Entry Point (CLI + Batch)
# =========================
if __name__ == "__main__":
    cities = ["pune", "hyderabad", "kolkata", "ahmedabad"]

    # -------------------------
    # Batch Mode (All Cities)
    # -------------------------
    if len(sys.argv) < 2:
        print("No city provided. Processing all cities...\n")

        for city in cities:
            input_path = f"../data/city-test-files/test_{city}.csv"
            output_path = f"results_{city}.csv"

            if not os.path.exists(input_path):
                print(f"Skipping {city} (file not found)")
                continue

            process_file(input_path, output_path)
            print(f"Done: {city}")

    # -------------------------
    # Single City Mode
    # -------------------------
    else:
        city = sys.argv[1].lower()

        input_path = f"../data/city-test-files/test_{city}.csv"
        output_path = f"results_{city}.csv"

        if not os.path.exists(input_path):
            print(f"Error: File not found for city '{city}'")
            sys.exit(1)

        process_file(input_path, output_path)
        print(f"Processing complete for {city}. Results saved.")