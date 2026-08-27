"""
UC-0C — Number That Looks Right

Explicit per-ward, per-category growth calculator for ward_budget.csv.
"""
import argparse
import csv
import re
import sys
from pathlib import Path


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_FIELDS = [
    "record_type",
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "previous_actual_spend",
    "growth_type",
    "growth_percent",
    "formula",
    "status",
    "notes",
]
LINE_PREFIX_RE = re.compile(r"^\s*\d+\|")
FORMULA = "((current_actual - previous_actual) / previous_actual) * 100"


def _clean_cell(value) -> str:
    if value is None:
        return ""
    return LINE_PREFIX_RE.sub("", str(value)).strip()


def _format_growth(value: float) -> str:
    return f"{value:+.1f}%"


def load_dataset(input_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Read the budget CSV and report all null actual_spend rows."""
    rows = []
    null_rows = []

    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        for row in reader:
            clean_row = {key: _clean_cell(row.get(key)) for key in REQUIRED_COLUMNS}
            rows.append(clean_row)
            if clean_row["actual_spend"] == "":
                null_rows.append(clean_row)

    return rows, null_rows


def compute_growth(
    rows: list[dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict[str, str]]:
    """Compute MoM growth for one explicit ward and category."""
    if not ward or not category:
        raise ValueError("Refusing all-ward or all-category aggregation: provide --ward and --category.")
    if not growth_type:
        raise ValueError("Refusing to guess formula: provide --growth-type MoM.")
    if growth_type != "MoM":
        raise ValueError("Only explicit --growth-type MoM is supported for this UC.")

    selected = [row for row in rows if row["ward"] == ward and row["category"] == category]
    if not selected:
        raise ValueError(f"No rows found for ward '{ward}' and category '{category}'.")

    selected.sort(key=lambda row: row["period"])
    output_rows = []
    previous_actual = ""

    for row in selected:
        status = "OK"
        growth_percent = ""
        formula = FORMULA

        if row["actual_spend"] == "":
            status = "NULL_ACTUAL"
        elif previous_actual == "":
            status = "NO_PREVIOUS" if not output_rows else "NULL_PREVIOUS"
        else:
            current_value = float(row["actual_spend"])
            previous_value = float(previous_actual)
            growth_percent = _format_growth(((current_value - previous_value) / previous_value) * 100)

        output_rows.append(
            {
                "record_type": "growth",
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": row["actual_spend"],
                "previous_actual_spend": previous_actual,
                "growth_type": growth_type,
                "growth_percent": growth_percent,
                "formula": formula if status == "OK" else "",
                "status": status,
                "notes": row["notes"],
            }
        )

        previous_actual = row["actual_spend"]

    return output_rows


def write_output(
    output_path: str,
    growth_rows: list[dict[str, str]],
    null_rows: list[dict[str, str]],
    growth_type: str,
):
    """Write growth rows and the complete null inventory to CSV."""
    existing_null_keys = {
        (row["period"], row["ward"], row["category"])
        for row in growth_rows
        if row["status"] == "NULL_ACTUAL"
    }
    null_inventory = []

    for row in null_rows:
        key = (row["period"], row["ward"], row["category"])
        if key in existing_null_keys:
            continue
        null_inventory.append(
            {
                "record_type": "null_flag",
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": "",
                "previous_actual_spend": "",
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "",
                "status": "NULL_ACTUAL",
                "notes": row["notes"],
            }
        )

    output_file_path = Path(output_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with output_file_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(growth_rows + null_inventory)


def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="Growth type, must be MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)
        growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
        write_output(args.output, growth_rows, null_rows, args.growth_type)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
