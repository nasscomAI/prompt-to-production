import csv
import argparse
from collections import defaultdict

def process_budget(input_path, output_path):
    data = defaultdict(lambda: defaultdict(float))

    try:
        with open(input_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    ward = row.get("ward", "").strip()
                    category = row.get("category", "").strip()
                    amount = float(row.get("amount", 0))

                    if not ward or not category:
                        continue

                    data[ward][category] += amount

                except:
                    continue

        with open(output_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ward", "category", "total_amount"])

            for ward in data:
                for category in data[ward]:
                    writer.writerow([ward, category, data[ward][category]])

        print("Budget processed ✅")

    except Exception as e:
        print("Error:", e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    process_budget(args.input, args.output)


if __name__ == "__main__":
    main()