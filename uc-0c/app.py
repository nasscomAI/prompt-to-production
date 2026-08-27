"""
UC-0C app.py — Number That Looks Right
"""
import argparse
import csv
import os
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(input_path: str) -> List[Dict[str, str]]:
    with open(input_path, "r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames or []
        missing = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows = list(reader)

    return rows


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Unsupported growth type. Use MoM or YoY.")

    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not filtered:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    results: List[Dict[str, str]] = []
    null_rows: List[Dict[str, str]] = []
    filtered.sort(key=lambda row: row["period"])

    previous_value: Optional[float] = None
    for row in filtered:
        actual = row["actual_spend"].strip()
        output_row = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"],
            "notes": row["notes"],
            "growth_type": growth_type,
            "formula": "",
            "growth": "",
            "null_flag": "",
        }

        if actual == "" or actual.upper() == "NULL":
            output_row["formula"] = "SKIPPED: NULL actual_spend"
            output_row["growth"] = "NULL"
            output_row["null_flag"] = row["notes"] or "Missing reason"
            null_rows.append(output_row)
            previous_value = None
        else:
            actual_value = float(actual)
            if growth_type == "MoM":
                formula = "(current - previous) / previous * 100"
                if previous_value is None:
                    growth_value = "N/A"
                    output_row["formula"] = "No prior month available or prior month null"
                else:
                    growth_value = f"{(actual_value - previous_value) / previous_value * 100:.1f}%"
                    output_row["formula"] = formula
                previous_value = actual_value
            else:
                raise ValueError("YoY growth is not implemented yet.")

            output_row["growth"] = growth_value
            output_row["null_flag"] = ""

        results.append(output_row)

    return results, null_rows


def write_output(output_path: str, rows: List[Dict[str, str]]):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
        "growth_type",
        "formula",
        "growth",
        "null_flag",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    results, null_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, results)

    print(f"Done. Output written to {args.output}")
    if null_rows:
        print(f"Null rows flagged: {len(null_rows)}")
        for null_row in null_rows:
            print(f"{null_row['period']} - {null_row['null_flag']}")


if __name__ == "__main__":
    main()
