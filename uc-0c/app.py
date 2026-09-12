import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(input_path):
    path = Path(input_path)
    if not path.is_file():
        raise ValueError(f"Input dataset does not exist: {input_path}")
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("Dataset is missing required columns")
        rows = list(reader)
    if not rows:
        raise ValueError("Input dataset is empty")
    for row in rows:
        try:
            row["budgeted_amount"] = float(row["budgeted_amount"])
            row["actual_spend"] = None if not row["actual_spend"].strip() else float(row["actual_spend"])
        except (AttributeError, ValueError) as error:
            raise ValueError(f"Invalid numeric value in period {row.get('period')}") from error
    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError("--growth-type is required; refusing to guess a formula")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: {growth_type}; only MoM is defined")
    if ward.lower() in {"all", "all wards", "*"} or category.lower() in {"all", "all categories", "*"}:
        raise ValueError("Refusing aggregation across wards or categories")
    selected = sorted(
        (row for row in rows if row["ward"] == ward and row["category"] == category),
        key=lambda row: row["period"],
    )
    if not selected:
        raise ValueError("No rows match the requested ward and category")
    output = []
    previous = None
    for row in selected:
        current = row["actual_spend"]
        result = dict(row)
        result["growth_type"] = growth_type
        result["formula"] = "((current - previous) / previous) * 100"
        if current is None:
            result["growth_percent"] = ""
            result["status"] = f"NOT_COMPUTED: missing actual_spend; {row['notes'] or 'no reason provided'}"
        elif previous is None or previous == 0:
            result["growth_percent"] = ""
            result["status"] = "NOT_COMPUTED: no prior non-null period"
        else:
            result["growth_percent"] = f"{((current - previous) / previous) * 100:.1f}"
            result["status"] = "COMPUTED"
        if current is not None:
            previous = current
        output.append(result)
    return output

def main():
    parser = argparse.ArgumentParser(description="Compute ward-level month-over-month growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    results = compute_growth(load_dataset(args.input), args.ward, args.category, args.growth_type)
    fields = ["period", "ward", "category", "actual_spend", "growth_type", "formula", "growth_percent", "status"]
    with Path(args.output).open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in results)

if __name__ == "__main__":
    main()
