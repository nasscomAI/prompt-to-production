import argparse
import csv


def calculate_growth(input_path, output_path):

    results = []

    with open(input_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                ward = row.get("ward")
                category = row.get("category")

                current = float(row.get("current_budget", 0))
                previous = float(row.get("previous_budget", 0))

                growth = current - previous

                results.append({
                    "ward": ward,
                    "category": category,
                    "growth": growth
                })

            except:
                results.append({
                    "ward": row.get("ward", "unknown"),
                    "category": row.get("category", "unknown"),
                    "growth": "ERROR"
                })

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        fieldnames = ["ward", "category", "growth"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    calculate_growth(args.input, args.output)

    print("Growth analysis complete.")