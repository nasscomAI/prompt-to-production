import argparse
import csv


def load_budget_data(file_path):
    """Load ward budget CSV file into structured records."""
    data = []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data.append(row)

    if not data:
        raise ValueError("Dataset is empty or unreadable")

    return data


def analyze_budget_metrics(data):
    """
    Compute total budget per ward.
    Automatically detects numeric column.
    """
    totals = {}

    for row in data:
        ward = row.get("ward")

        if ward is None:
            raise ValueError("Column 'ward' missing in dataset")

        # detect numeric column automatically
        amount = None
        for value in row.values():
            try:
                amount = float(value)
                break
            except:
                continue

        if amount is None:
            raise ValueError("No numeric budget value found")

        totals[ward] = totals.get(ward, 0) + amount

    return totals


def write_results(results, output_path):
    """Write computed metrics to output file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in results.items():
            f.write(f"{key}: {value}\n")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write results")

    args = parser.parse_args()

    data = load_budget_data(args.input)
    results = analyze_budget_metrics(data)

    write_results(results, args.output)

    print(f"Analysis written to {args.output}")


if __name__ == "__main__":
    main()