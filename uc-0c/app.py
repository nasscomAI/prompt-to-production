"""
UC-0C — Budget growth computation agent.
Reads a ward budget CSV, filters to a single ward + category, computes MoM or YoY
growth per period, shows formula in every row, and flags null actual_spend values.
Never aggregates across wards or categories.
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Budget file not found: {path.resolve()}")

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row")
        headers = set(reader.fieldnames)
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    if not rows:
        print("Warning: CSV file contains no data rows.", file=sys.stderr)
        return []

    null_rows = [r for r in rows if r.get("actual_spend", "").strip() == ""]
    if null_rows:
        print(f"Found {len(null_rows)} row(s) with null actual_spend:", file=sys.stderr)
        for nr in null_rows:
            note = nr.get("notes", "").strip()
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} — {note}", file=sys.stderr)

    return rows


def compute_growth(rows, growth_type):
    if growth_type == "YoY":
        raise ValueError(
            "YoY growth requires multi-year data. The input dataset contains only "
            "2024 records. Use --growth-type MoM instead."
        )

    rows_sorted = sorted(rows, key=lambda r: r["period"])
    output = []

    for i, row in enumerate(rows_sorted):
        actual_raw = row.get("actual_spend", "").strip()
        is_null = actual_raw == ""
        actual = None if is_null else float(actual_raw)

        if is_null:
            note = row.get("notes", "").strip()
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": "",
                "previous_period_actual": "N/A",
                "growth_percent": "N/A",
                "formula_used": "N/A — actual_spend is null",
                "null_flag": "YES",
                "null_reason": note,
            })
            continue

        if i == 0:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": f"{actual:.1f}",
                "previous_period_actual": "N/A",
                "growth_percent": "N/A",
                "formula_used": "N/A — first period has no previous period",
                "null_flag": "",
                "null_reason": "",
            })
            continue

        prev_raw = rows_sorted[i - 1].get("actual_spend", "").strip()
        if prev_raw == "":
            growth_pct = "N/A"
            formula = f"N/A — previous period ({rows_sorted[i - 1]['period']}) has null actual_spend"
        else:
            prev_actual = float(prev_raw)
            growth_pct = ((actual - prev_actual) / prev_actual) * 100
            formula = (
                f"(({row['period']} actual - {rows_sorted[i - 1]['period']} actual) "
                f"/ {rows_sorted[i - 1]['period']} actual) * 100"
            )

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": f"{actual:.1f}",
            "previous_period_actual": f"{prev_actual:.1f}" if prev_raw != "" else "N/A",
            "growth_percent": f"{growth_pct:+.1f}%" if isinstance(growth_pct, float) else growth_pct,
            "formula_used": formula,
            "null_flag": "",
            "null_reason": "",
        })

    return output


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C: Budget growth computation agent"
    )
    parser.add_argument("--input", required=True, help="Path to the input budget CSV")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV")
    parser.add_argument("--ward", required=True, help="Ward name to filter (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category to filter (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    args = parser.parse_args()

    if not args.growth_type:
        print("Error: --growth-type is required. Allowed values: MoM, YoY", file=sys.stderr)
        sys.exit(1)

    try:
        all_rows = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    filtered = [
        r for r in all_rows
        if r["ward"] == args.ward and r["category"] == args.category
    ]

    if not filtered:
        print(
            f"Error: No rows found for ward '{args.ward}' and category '{args.category}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = compute_growth(filtered, args.growth_type)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "period", "ward", "category", "budgeted_amount", "actual_spend",
        "previous_period_actual", "growth_percent", "formula_used",
        "null_flag", "null_reason",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Growth output written to {output_path.resolve()}")
    print(f"Rows: {len(result)}")


if __name__ == "__main__":
    main()
