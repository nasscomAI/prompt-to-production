import argparse
import csv
import sys

REQUIRED_COLUMNS = [
    "ward",
    "category",
    "period",
    "actual_spend",
    "notes"
]


def read_csv_safely(file_path):
    """Read CSV safely and validate required columns."""
    try:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or missing header.")

            missing_cols = [
                col for col in REQUIRED_COLUMNS
                if col not in reader.fieldnames
            ]

            if missing_cols:
                raise ValueError(
                    f"Missing required columns: {', '.join(missing_cols)}"
                )

            return list(reader)

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except PermissionError:
        print(f"Error: Permission denied: {file_path}")
    except ValueError as e:
        print(f"Data Error: {e}")
    except Exception as e:
        print(f"Unexpected error while reading file: {e}")

    return None


def parse_float(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def filter_rows(rows, ward, category):
    return [
        row for row in rows
        if str(row.get("ward", "")).strip().lower() == ward.lower()
        and str(row.get("category", "")).strip().lower() == category.lower()
    ]


def compute_mom_growth(filtered_rows):
    results = []

    previous_value = None
    previous_period = None

    for row in filtered_rows:
        period = row.get("period", "")
        spend = parse_float(row.get("actual_spend"))
        notes = row.get("notes", "").strip()

        output_row = {
            "ward": row.get("ward", ""),
            "category": row.get("category", ""),
            "period": period,
            "actual_spend": row.get("actual_spend", ""),
            "growth_type": "MoM",
            "growth_percent": "",
            "formula": "",
            "flag": "",
            "reason": ""
        }

        if spend is None:
            output_row["flag"] = "NEEDS_REVIEW"
            output_row["reason"] = notes if notes else "actual_spend is null"
            results.append(output_row)
            continue

        if previous_value is None:
            output_row["flag"] = "BASELINE"
            output_row["reason"] = "No previous period available for MoM calculation."
            results.append(output_row)

            previous_value = spend
            previous_period = period
            continue

        if previous_value == 0:
            output_row["flag"] = "NEEDS_REVIEW"
            output_row["reason"] = f"Previous period's spend ({previous_period}) is zero."
            results.append(output_row)

            previous_value = spend
            previous_period = period
            continue

        growth = ((spend - previous_value) / previous_value) * 100

        output_row["growth_percent"] = round(growth, 2)
        output_row["formula"] = f"(({spend} - {previous_value}) / {previous_value}) * 100 = {round(growth, 2)}"

        results.append(output_row)

        previous_value = spend
        previous_period = period

    return results


def write_output(output_path, rows):
    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "flag",
        "reason"
    ]

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                writer.writerow(row)

        print(f"Results written to {output_path}")

    except Exception as e:
        print(f"Error writing output file: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type.lower() != "mom":
        print("Error: Only MoM growth is supported.")
        sys.exit(1)

    rows = read_csv_safely(args.input)

    if rows is None:
        sys.exit(1)

    filtered_rows = filter_rows(rows, args.ward, args.category)

    if not filtered_rows:
        print("No matching rows found for the specified ward and category.")
        sys.exit(1)

    results = compute_mom_growth(filtered_rows)

    write_output(args.output, results)


if __name__ == "__main__":
    main()