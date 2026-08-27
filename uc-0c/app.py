"""
UC-0C — Growth Calculation for Budget Data.

The script reads the ward budget CSV, computes month-over-month growth for a
single ward/category pair, flags null rows before computation, and writes a
per-period CSV. It refuses all-ward aggregation or missing growth-type input.
"""
import argparse
import csv
from pathlib import Path
from typing import List, Dict


def load_dataset(input_path: str) -> List[Dict[str, str]]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))

    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if not required.issubset(rows[0].keys()):
        raise ValueError("Dataset is missing one or more required columns")
    return rows


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    if not ward or not category:
        raise ValueError("A specific ward and category are required; all-ward aggregation is not allowed.")
    if growth_type != "MoM":
        raise ValueError("Growth type must be specified as MoM; other growth types are not permitted.")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    filtered.sort(key=lambda row: row.get("period", ""))

    output_rows: List[Dict[str, str]] = []
    previous_actual = None
    previous_period = None
    for row in filtered:
        period = row.get("period", "")
        actual_spend = (row.get("actual_spend") or "").strip()
        if not actual_spend:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth_pct": "",
                "formula": "NULL row — not computed",
                "status": "FLAGGED_NULL",
                "notes": row.get("notes", ""),
            })
            previous_actual = None
            previous_period = None
            continue

        actual_value = float(actual_spend)
        if previous_actual is None:
            growth_pct = ""
            formula = "N/A (first period)"
        else:
            if previous_actual == 0:
                growth_pct = ""
                formula = "Division by zero — not computed"
            else:
                growth_pct = f"{((actual_value - previous_actual) / previous_actual) * 100:.1f}%"
                formula = f"(({actual_value} - {previous_actual}) / {previous_actual}) * 100"
        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual_value:.1f}",
            "growth_pct": growth_pct,
            "formula": formula,
            "status": "COMPUTED",
            "notes": row.get("notes", ""),
        })
        previous_actual = actual_value
        previous_period = period
    return output_rows


def write_output(output_path: str, rows: List[Dict[str, str]]) -> None:
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fields = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "status", "notes"]
    with output_file.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C growth calculation")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name; all-ward aggregation is not allowed")
    parser.add_argument("--category", required=True, help="Category name; aggregation across categories is not allowed")
    parser.add_argument("--growth-type", required=True, help="Growth type; must be MoM")
    parser.add_argument("--output", required=True, help="Path to the output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, output_rows)
    print(f"Wrote {len(output_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
