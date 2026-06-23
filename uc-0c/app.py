"""
UC-0C app.py — Ward budget growth calculation tool.
"""
import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def parse_float(value):
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid numeric value: {value}")


def load_dataset(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    rows = []
    with path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            actual_spend = parse_float(row.get("actual_spend"))
            rows.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": parse_float(row.get("budgeted_amount")),
                "actual_spend": actual_spend,
                "notes": (row.get("notes") or "").strip(),
            })

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"Loaded {len(rows)} rows from {path}. Null actual_spend rows: {len(null_rows)}.")
    if null_rows:
        print("Flagged null rows:")
        for row in null_rows:
            print(f"  {row['period']} · {row['ward']} · {row['category']} -> {row['notes'] or 'No note provided'}")

    return rows


def compute_growth(rows, growth_type):
    sorted_rows = sorted(rows, key=lambda row: row["period"])
    output = []
    previous_actual = None

    for row in sorted_rows:
        actual = row["actual_spend"]
        prior = previous_actual
        if actual is None:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "NULL",
                "previous_actual_spend": "NULL" if prior is None else f"{prior:.1f}",
                "growth_pct": "FLAGGED",
                "formula": "NULL actual_spend, not computed",
                "note": row["notes"] or "No note provided",
            })
            previous_actual = None
            continue

        if prior is None:
            growth_pct = "N/A"
            formula = "No prior period available for growth calculation"
        elif prior == 0:
            growth_pct = "undefined"
            formula = "Division by zero in prior period actual_spend"
        else:
            if growth_type == "MoM":
                change = ((actual - prior) / prior) * 100
                growth_pct = f"{change:+.1f}%"
                formula = f"({actual:.1f} - {prior:.1f}) / {prior:.1f} * 100"
            else:
                growth_pct = "N/A"
                formula = "Unsupported growth type"

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": f"{actual:.1f}",
            "previous_actual_spend": "" if prior is None else f"{prior:.1f}",
            "growth_pct": growth_pct,
            "formula": formula,
            "note": "",
        })
        previous_actual = actual

    return output


def main():
    parser = argparse.ArgumentParser(description="Compute ward budget growth for a single ward and category.")
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV file.")
    parser.add_argument("--ward", required=True, help="Ward name to analyze.")
    parser.add_argument("--category", required=True, help="Category name to analyze.")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth type to compute.")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV file.")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    filtered = [row for row in rows if row["ward"] == args.ward and row["category"] == args.category]
    if not filtered:
        raise ValueError(f"No rows found for ward '{args.ward}' and category '{args.category}'.")

    if args.growth_type == "YoY":
        print("Note: YoY growth is not available because the dataset spans a single calendar year.")

    output_rows = compute_growth(filtered, args.growth_type)
    output_path = Path(args.output)
    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "period",
            "ward",
            "category",
            "actual_spend",
            "previous_actual_spend",
            "growth_pct",
            "formula",
            "note",
        ])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Growth output written to {output_path}")


if __name__ == "__main__":
    main()
