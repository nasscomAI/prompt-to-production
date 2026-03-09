import csv
import argparse


def load_dataset(file_path):
    rows = []
    null_rows = []

    with open(file_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            spend = row["actual_spend"]

            if spend == "" or spend.lower() == "null":
                null_rows.append(row)
            else:
                rows.append(row)

    return rows, null_rows


def compute_growth(rows):
    results = []
    previous = None

    for row in rows:
        spend = float(row["actual_spend"])

        if previous is None:
            growth = ""
            formula = "First period - no growth"
        else:
            growth = ((spend - previous) / previous) * 100
            formula = f"(({spend} - {previous}) / {previous}) * 100"

        results.append({
            "ward": row["ward"],
            "category": row["category"],
            "period": row["period"],
            "spend": spend,
            "growth_percent": growth,
            "formula": formula
        })

        previous = spend

    return results


def write_output(results, null_rows, output_file):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["ward", "category", "period", "spend", "growth_percent", "formula"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for row in results:
            writer.writerow(row)

        for row in null_rows:
            writer.writerow({
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "spend": "NULL",
                "growth_percent": "FLAGGED",
                "formula": "Missing spend value"
            })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows)
    write_output(results, null_rows, args.output)

    print("Growth analysis completed.")