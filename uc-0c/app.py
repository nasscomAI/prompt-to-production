import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
MOM_FORMULA = "((current - previous) / previous) * 100"


def load_dataset(filepath):
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows = list(reader)

    null_rows = [r for r in rows if not r["actual_spend"] or r["actual_spend"].strip() == ""]
    if null_rows:
        print("Null actual_spend rows found:", file=sys.stderr)
        for r in null_rows:
            note = r["notes"].strip() if r["notes"] else "(no note)"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | {note}", file=sys.stderr)

    if len(null_rows) == len(rows):
        print("WARNING: Every row has null actual_spend — growth cannot be computed.", file=sys.stderr)

    return rows


def compute_growth(rows, ward, category, growth_type):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError("--growth-type must be 'MoM' or 'YoY'")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'")

    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, r in enumerate(filtered):
        prev = None
        if growth_type == "MoM":
            if i > 0:
                prev = filtered[i - 1]
            formula = MOM_FORMULA
        else:
            if i >= 12:
                prev = filtered[i - 12]
            formula = "((current - previous_12mo) / previous_12mo) * 100"

        actual = r["actual_spend"].strip() if r["actual_spend"] else ""
        prev_actual = prev["actual_spend"].strip() if prev and prev["actual_spend"] else ""
        note = r["notes"].strip() if r["notes"] else ""

        row = {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "actual_spend": actual if actual else "",
            "previous_spend": prev_actual if prev_actual else "",
            "growth_pct": "",
            "formula": formula,
            "null_flag": "",
        }

        if not actual:
            row["null_flag"] = note if note else "NULL — not computed"
        elif not prev_actual:
            row["null_flag"] = "insufficient data — no prior period"
        else:
            current_val = float(actual)
            prev_val = float(prev_actual)
            if prev_val != 0:
                row["growth_pct"] = round(((current_val - prev_val) / prev_val) * 100, 2)
            else:
                row["null_flag"] = "previous spend is zero — cannot divide"

        results.append(row)

    return results


def main():
    parser = argparse.ArgumentParser(description="Compute per-ward, per-category growth metrics.")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Growth type: MoM or YoY")
    parser.add_argument("--output", default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    if not args.growth_type:
        print("--growth-type is required (MoM or YoY)", file=sys.stderr)
        sys.exit(1)

    try:
        rows = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"Error computing growth: {e}", file=sys.stderr)
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "previous_spend", "growth_pct", "formula", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
