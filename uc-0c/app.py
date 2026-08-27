"""
UC-0C app.py — Number That Looks Right
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from pathlib import Path
from typing import List, Dict, Optional


def load_dataset(input_path: str) -> List[Dict[str, str]]:
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with path.open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [dict(row) for row in reader]

    required_columns = {
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    }
    missing = required_columns - set(rows[0].keys()) if rows else required_columns
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    return rows


def parse_float(value: str) -> Optional[float]:
    value = value.strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def filter_dataset(rows: List[Dict[str, str]], ward: str, category: str) -> List[Dict[str, str]]:
    filtered = [
        row for row in rows
        if row["ward"].strip() == ward.strip() and row["category"].strip() == category.strip()
    ]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")
    return sorted(filtered, key=lambda row: row["period"])


def compute_growth(rows: List[Dict[str, str]], growth_type: str) -> List[Dict[str, str]]:
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: {growth_type}. Only 'MoM' is supported.")

    output = []
    previous_actual = None
    previous_period = None

    for row in rows:
        actual = parse_float(row["actual_spend"])
        budgeted = parse_float(row["budgeted_amount"])
        notes = row.get("notes", "").strip()
        flag = ""
        formula = ""
        growth = ""

        if actual is None:
            flag = "NEEDS_REVIEW"
            formula = "Cannot compute MoM growth because actual_spend is NULL."
        elif previous_actual is None:
            formula = "MoM growth cannot be computed for the first available period or when prior actual_spend is missing."
        else:
            if previous_actual == 0:
                growth = "INF"
                formula = (
                    "MoM growth = (current_actual - previous_actual) / previous_actual * 100, "
                    f"but previous_actual is 0 for {previous_period}."
                )
            else:
                pct = (actual - previous_actual) / previous_actual * 100
                growth = f"{pct:+.1f}%"
                formula = (
                    "MoM growth = (current_actual - previous_actual) / previous_actual * 100 "
                    f"= ({actual:.1f} - {previous_actual:.1f}) / {previous_actual:.1f} * 100"
                )

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": f"{budgeted:.1f}" if budgeted is not None else "",
            "actual_spend": f"{actual:.1f}" if actual is not None else "",
            "notes": notes,
            "growth_type": growth_type,
            "growth": growth,
            "formula": formula,
            "flag": flag,
        })

        previous_actual = actual if actual is not None else previous_actual
        previous_period = row["period"]

    return output


def write_output(rows: List[Dict[str, str]], output_path: str) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
        "growth_type",
        "growth",
        "formula",
        "flag",
    ]
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C growth calculator for a specific ward and category."
    )
    parser.add_argument("--input", required=True, help="Path to the ward budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name to analyze")
    parser.add_argument("--category", required=True, help="Category to analyze")
    parser.add_argument("--growth-type", required=True, help="Type of growth to compute (MoM)")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    filtered_rows = filter_dataset(rows, args.ward, args.category)
    output_rows = compute_growth(filtered_rows, args.growth_type)
    write_output(output_rows, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
