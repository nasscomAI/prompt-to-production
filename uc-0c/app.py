"""
UC-0C - Number That Looks Right.
Computes period-over-period growth only for one explicit ward and category.
"""
import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}
SUPPORTED_GROWTH_TYPES = {"MoM"}


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_amount(value):
    if value is None or value.strip() == "":
        return None
    return float(value)


def load_dataset(input_path):
    path = Path(input_path)
    if not path.exists():
        fail(f"Input file not found: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            fail(f"Input file is missing required columns: {', '.join(sorted(missing))}")

        rows = list(reader)

    null_rows = [
        row
        for row in rows
        if row.get("actual_spend") is None or row["actual_spend"].strip() == ""
    ]

    print(f"Loaded {len(rows)} rows from {input_path}")
    print(f"Null actual_spend rows: {len(null_rows)}")
    for row in null_rows:
        reason = row.get("notes", "").strip() or "No note provided"
        print(
            "NULL FLAG: "
            f"{row['period']} | {row['ward']} | {row['category']} | {reason}"
        )

    return rows


def require_explicit_filters(ward, category, growth_type):
    if not ward:
        fail("Ward is required. Refusing to aggregate across wards.")
    if not category:
        fail("Category is required. Refusing to aggregate across categories.")
    if not growth_type:
        fail("Growth type is required. Specify --growth-type; do not rely on a guess.")
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        fail(
            f"Unsupported growth type '{growth_type}'. "
            f"Supported values: {', '.join(sorted(SUPPORTED_GROWTH_TYPES))}"
        )


def format_growth(value):
    if value is None:
        return ""
    return f"{value:+.1f}%"


def compute_growth(rows, ward, category, growth_type):
    require_explicit_filters(ward, category, growth_type)

    filtered = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]
    if not filtered:
        fail(f"No rows found for ward '{ward}' and category '{category}'")

    filtered.sort(key=lambda row: row["period"])

    output_rows = []
    previous_actual = None
    previous_period = None

    for row in filtered:
        actual = parse_amount(row["actual_spend"])
        notes = row.get("notes", "").strip()

        if actual is None:
            growth = None
            formula = f"Not computed: actual_spend is NULL ({notes or 'No note provided'})"
            status = "NULL_ACTUAL_SPEND"
        elif previous_actual is None:
            growth = None
            formula = "Not computed: no prior non-null actual_spend in this ward/category"
            status = "NO_PRIOR_PERIOD"
        elif previous_actual == 0:
            growth = None
            formula = f"Not computed: prior actual_spend for {previous_period} is 0"
            status = "ZERO_PRIOR_ACTUAL"
        else:
            growth = ((actual - previous_actual) / previous_actual) * 100
            formula = (
                f"(({actual:.1f} - {previous_actual:.1f}) / "
                f"{previous_actual:.1f}) * 100"
            )
            status = "OK"

        output_rows.append(
            {
                "ward": row["ward"],
                "category": row["category"],
                "period": row["period"],
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": "" if actual is None else f"{actual:.1f}",
                "growth_type": growth_type,
                "growth": format_growth(growth),
                "formula": formula,
                "status": status,
                "notes": notes,
            }
        )

        if actual is not None:
            previous_actual = actual
            previous_period = row["period"]

    return output_rows


def write_output(rows, output_path):
    fieldnames = [
        "ward",
        "category",
        "period",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth",
        "formula",
        "status",
        "notes",
    ]
    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_path}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Compute growth for one explicit ward and category."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name to compute")
    parser.add_argument("--category", help="Exact category name to compute")
    parser.add_argument("--growth-type", choices=sorted(SUPPORTED_GROWTH_TYPES))
    parser.add_argument("--output", required=True, help="Output CSV path")
    return parser


def main():
    args = build_parser().parse_args()
    rows = load_dataset(args.input)
    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(growth_rows, args.output)


if __name__ == "__main__":
    main()
