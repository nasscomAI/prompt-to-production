
import csv
import argparse
import sys


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(file_path):
    data = []
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # Validate columns
            if not all(col in reader.fieldnames for col in REQUIRED_COLUMNS):
                missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
                print(f"Error: Missing columns: {missing}")
                sys.exit(1)

            for row in reader:
                # Clean and parse
                actual = row["actual_spend"].strip()
                if actual == "":
                    row["actual_spend"] = None
                    null_rows.append(row)
                else:
                    row["actual_spend"] = float(actual)

                row["budgeted_amount"] = float(row["budgeted_amount"])
                data.append(row)

        # Report nulls
        if null_rows:
            print(f"Found {len(null_rows)} null rows:")
            for r in null_rows:
                print(f"{r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")

        return data

    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(1)


def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        print("Error: growth-type must be specified (e.g., MoM)")
        sys.exit(1)

    if growth_type != "MoM":
        print("Error: Only MoM growth is supported. Refusing to assume.")
        sys.exit(1)

    # Filter strictly
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]

    if not filtered:
        print("Error: No data found for given ward and category")
        sys.exit(1)

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev = None

    for row in filtered:
        current_value = row["actual_spend"]

        result_row = {
            "period": row["period"],
            "ward": ward,
            "category": category,
            "actual_spend": current_value,
            "growth": "",
            "formula": "",
            "note": ""
        }

        # Handle null
        if current_value is None:
            result_row["growth"] = "NULL"
            result_row["formula"] = "Not computed due to null actual_spend"
            result_row["note"] = row["notes"]
            results.append(result_row)
            prev = None
            continue

        if prev is None:
            result_row["growth"] = "N/A"
            result_row["formula"] = "No previous month to compare"
        else:
            if prev["actual_spend"] is None:
                result_row["growth"] = "NULL"
                result_row["formula"] = "Previous value null, cannot compute"
                result_row["note"] = prev["notes"]
            else:
                prev_val = prev["actual_spend"]
                curr_val = current_value

                growth = ((curr_val - prev_val) / prev_val) * 100

                result_row["growth"] = f"{growth:.2f}%"
                result_row["formula"] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"

        results.append(result_row)
        prev = row

    return results


def write_output(file_path, results):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "note"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    write_output(args.output, results)

    print(f"Output written to {args.output}")


if __name__ == "__main__":
    main()