"""
UC-0C budgeting growth calculator.
This app reads the ward budget dataset, enforces the rules in agents.md and skills.md,
and writes a per-ward per-category growth table to a CSV file.
"""
import argparse
import csv
from pathlib import Path
from typing import Dict, List

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(file_path: str) -> List[Dict[str, object]]:
    """Load and validate the ward budget CSV."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("The input CSV is empty or missing a header row.")

        missing_columns = sorted(REQUIRED_COLUMNS - set(reader.fieldnames))
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        rows: List[Dict[str, object]] = []
        for row in reader:
            normalized_row: Dict[str, object] = {
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": float(row.get("budgeted_amount", "0") or 0),
                "actual_spend": None if not str(row.get("actual_spend", "")).strip() else float(row.get("actual_spend")),
                "notes": (row.get("notes") or "").strip(),
            }
            rows.append(normalized_row)

    return rows


def compute_growth(rows: List[Dict[str, object]], ward: str, category: str, growth_type: str) -> List[Dict[str, object]]:
    """Compute growth for one ward/category across ordered periods."""
    matching_rows = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not matching_rows:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    matching_rows = sorted(matching_rows, key=lambda row: str(row["period"]))

    results: List[Dict[str, object]] = []
    previous_row: Dict[str, object] | None = None

    for current_row in matching_rows:
        period = str(current_row["period"])
        current_actual = current_row["actual_spend"]
        notes = str(current_row.get("notes", ""))

        if current_actual is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_value": "",
                    "formula": "",
                    "status": "NULL_ROW",
                    "notes": notes if notes else "No note provided",
                }
            )
            previous_row = current_row
            continue

        if growth_type not in {"MoM", "YoY"}:
            raise ValueError("Growth type must be either MoM or YoY.")

        if previous_row is None:
            growth_value = ""
            formula = "n/a (first period)"
            status = "INSUFFICIENT_DATA"
        else:
            previous_actual = previous_row["actual_spend"]
            if previous_actual is None or previous_actual == 0:
                growth_value = ""
                formula = "n/a (previous actual spend missing or zero)"
                status = "INSUFFICIENT_DATA"
            else:
                if growth_type == "MoM":
                    growth_value = ((float(current_actual) - float(previous_actual)) / float(previous_actual)) * 100
                    formula = f"((current - previous) / previous) * 100 = ({float(current_actual)} - {float(previous_actual)}) / {float(previous_actual)} * 100"
                    status = "OK"
                else:
                    growth_value = ""
                    formula = "n/a (previous year not available in this dataset)"
                    status = "INSUFFICIENT_DATA"

        results.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": float(current_actual),
                "growth_value": "" if growth_value == "" else round(float(growth_value), 2),
                "formula": formula,
                "status": status if "status" in locals() else "OK",
                "notes": notes if notes else "",
            }
        )
        previous_row = current_row

    return results


def write_output_csv(rows: List[Dict[str, object]], output_path: str) -> None:
    """Write the computed growth rows to a CSV file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_value", "formula", "status", "notes"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(input_path: str, ward: str, category: str, growth_type: str, output_path: str) -> Dict[str, object]:
    """Run the full pipeline for one ward/category request."""
    rows = load_dataset(input_path)
    results = compute_growth(rows, ward, category, growth_type)
    write_output_csv(results, output_path)
    return {"ward": ward, "category": category, "growth_type": growth_type, "rows": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C budgeting growth calculator")
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name to analyze")
    parser.add_argument("--category", required=True, help="Category name to analyze")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write the output CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("Refusal: growth type not specified. Please provide --growth-type MoM or --growth-type YoY.")
        return

    run_pipeline(args.input, args.ward, args.category, args.growth_type, args.output)
    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()
