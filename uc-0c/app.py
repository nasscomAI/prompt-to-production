"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
from typing import Any, Dict, List

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(input_csv_path: str) -> Dict[str, Any]:
    if not os.path.isfile(input_csv_path):
        raise FileNotFoundError(f"Input file not found: {input_csv_path}")

    with open(input_csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        rows: List[Dict[str, str]] = []
        null_rows: List[Dict[str, str]] = []
        for row in reader:
            rows.append(row)
            if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                null_rows.append({
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": row.get("notes", ""),
                })

    null_count = len(null_rows)
    print(f"Loaded {len(rows)} rows from {input_csv_path}.")
    print(f"Found {null_count} rows with null actual_spend.")
    if null_count > 0:
        print("Null rows:")
        for null_row in null_rows:
            print(f"  {null_row['period']} · {null_row['ward']} · {null_row['category']} · notes: {null_row['notes']}")

    return {
        "rows": rows,
        "null_count": null_count,
        "null_rows": null_rows,
    }


def parse_float(value: str) -> float:
    return float(value.replace(",", ""))


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> Dict[str, Any]:
    if not ward:
        raise ValueError("Ward is required")
    if not category:
        raise ValueError("Category is required")
    if not growth_type:
        raise ValueError("Growth type is required")
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"Unsupported growth type: {growth_type}")

    filtered = [row for row in rows if row.get("ward") == ward and row.get("category") == category]
    filtered.sort(key=lambda row: row.get("period", ""))

    results: List[Dict[str, str]] = []
    previous_values: Dict[str, float] = {}

    for row in filtered:
        period = row.get("period", "")
        actual_spend_raw = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        if actual_spend_raw == "":
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "",
                "formula": "Null actual_spend — growth not computed",
                "notes": notes or "actual_spend is missing",
            })
            continue

        try:
            actual_spend = parse_float(actual_spend_raw)
        except ValueError:
            results.append({
                "period": period,
                "actual_spend": actual_spend_raw,
                "growth": "",
                "formula": f"Unable to parse actual_spend '{actual_spend_raw}'",
                "notes": notes or "invalid actual_spend value",
            })
            continue

        if growth_type == "MoM":
            prev_value = previous_values.get("MoM")
            if prev_value is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "growth": "",
                    "formula": "MoM growth requires the previous period's actual_spend",
                    "notes": "First valid period or previous actual_spend missing",
                })
            else:
                if prev_value == 0.0:
                    growth_str = "N/A"
                    formula = "MoM growth cannot be computed because previous actual_spend is zero"
                else:
                    growth_rate = (actual_spend - prev_value) / prev_value * 100
                    sign = "+" if growth_rate >= 0 else ""
                    growth_str = f"{sign}{growth_rate:.1f}%"
                    formula = (
                        f"MoM growth = ({actual_spend:.1f} - {prev_value:.1f}) / {prev_value:.1f}"
                    )
                results.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "growth": growth_str,
                    "formula": formula,
                    "notes": notes,
                })
            if actual_spend_raw != "":
                previous_values["MoM"] = actual_spend
        elif growth_type == "YoY":
            prior_period = None
            if len(period) == 7 and period[:4].isdigit() and period[5] == "-":
                prior_period = f"{int(period[:4]) - 1}{period[4:]}"
            prev_value = None
            if prior_period:
                for prev_row in filtered:
                    if prev_row.get("period") == prior_period:
                        prev_raw = prev_row.get("actual_spend", "").strip()
                        if prev_raw:
                            try:
                                prev_value = parse_float(prev_raw)
                            except ValueError:
                                prev_value = None
                        break

            if prev_value is None:
                results.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "growth": "",
                    "formula": "YoY growth requires prior-year period with non-null actual_spend",
                    "notes": notes,
                })
            else:
                if prev_value == 0.0:
                    growth_str = "N/A"
                    formula = "YoY growth cannot be computed because prior-year actual_spend is zero"
                else:
                    growth_rate = (actual_spend - prev_value) / prev_value * 100
                    sign = "+" if growth_rate >= 0 else ""
                    growth_str = f"{sign}{growth_rate:.1f}%"
                    formula = (
                        f"YoY growth = ({actual_spend:.1f} - {prev_value:.1f}) / {prev_value:.1f}"
                    )
                results.append({
                    "period": period,
                    "actual_spend": f"{actual_spend:.1f}",
                    "growth": growth_str,
                    "formula": formula,
                    "notes": notes,
                })
        else:
            raise ValueError(f"Unsupported growth type: {growth_type}")

    return {"results": results}


def write_output(output_path: str, results: List[Dict[str, str]]) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["period", "actual_spend", "growth", "formula", "notes"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({
                "period": row.get("period", ""),
                "actual_spend": row.get("actual_spend", ""),
                "growth": row.get("growth", ""),
                "formula": row.get("formula", ""),
                "notes": row.get("notes", ""),
            })


def main():
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset["rows"], args.ward, args.category, args.growth_type)
    write_output(args.output, results["results"])
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
