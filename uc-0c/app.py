import argparse
import csv
import sys
from datetime import date
from pathlib import Path

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}
OUTPUT_COLUMNS = [
    "period",
    "ward",
    "category",
    "actual_spend",
    "growth_type",
    "formula",
    "growth_percent",
    "status",
    "null_reason",
]


def load_dataset(input_path):
    """Load and validate the CSV while preserving blank actual_spend values."""
    path = Path(input_path)
    if not path.is_file():
        raise ValueError("Input file not found: {}".format(input_path))

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames or [])
            missing = sorted(REQUIRED_COLUMNS - headers)
            if missing:
                raise ValueError(
                    "Missing required column(s): {}".format(", ".join(missing))
                )

            rows = []
            null_rows = []
            for row_number, row in enumerate(reader, start=2):
                actual_text = (row["actual_spend"] or "").strip()
                actual_spend = None if actual_text == "" else float(actual_text)
                budgeted_amount = float(row["budgeted_amount"])
                record = {
                    "period": row["period"].strip(),
                    "ward": row["ward"].strip(),
                    "category": row["category"].strip(),
                    "budgeted_amount": budgeted_amount,
                    "actual_spend": actual_spend,
                    "notes": (row["notes"] or "").strip(),
                    "row_number": row_number,
                }
                rows.append(record)
                if actual_spend is None:
                    null_rows.append(record)
    except (OSError, csv.Error, TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("Missing required"):
            raise
        raise ValueError("Unable to read valid budget data: {}".format(exc)) from exc

    print(
        "Loaded {} rows; found {} null actual_spend row(s).".format(
            len(rows), len(null_rows)
        ),
        file=sys.stderr,
    )
    for record in null_rows:
        print(
            "NULL actual_spend: {} | {} | {} | reason: {}".format(
                record["period"],
                record["ward"],
                record["category"],
                record["notes"] or "not provided",
            ),
            file=sys.stderr,
        )
    return rows


def _period_date(period):
    try:
        year, month = (int(part) for part in period.split("-"))
        return date(year, month, 1)
    except (ValueError, TypeError):
        raise ValueError("Invalid period {}; expected YYYY-MM".format(period))


def _is_previous_month(previous_period, current_period):
    previous = _period_date(previous_period)
    current = _period_date(current_period)
    return (current.year * 12 + current.month) - (
        previous.year * 12 + previous.month
    ) == 1


def compute_growth(rows, ward, category, growth_type):
    """Return MoM growth rows for exactly one ward-category series."""
    if growth_type != "MoM":
        raise ValueError("Invalid --growth-type {!r}; supported value is MoM.".format(growth_type))

    selected = sorted(
        (row for row in rows if row["ward"] == ward and row["category"] == category),
        key=lambda row: _period_date(row["period"]),
    )
    if not selected:
        raise ValueError(
            "No records found for ward {!r} and category {!r}.".format(ward, category)
        )

    results = []
    previous = None
    for row in selected:
        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend"],
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": None,
            "status": "computed",
            "null_reason": "",
        }
        if row["actual_spend"] is None:
            result["formula"] = "Not computed: current actual_spend is NULL"
            result["status"] = "flagged_null"
            result["null_reason"] = row["notes"] or "not provided"
        elif previous is None:
            result["formula"] = "Not computed: no previous period"
            result["status"] = "not_applicable"
        elif not _is_previous_month(previous["period"], row["period"]):
            result["formula"] = "Not computed: previous period is not consecutive"
            result["status"] = "not_computed"
        elif previous["actual_spend"] is None:
            result["formula"] = (
                "Not computed: previous actual_spend is NULL ({})".format(
                    previous["notes"] or "reason not provided"
                )
            )
            result["status"] = "not_computed"
        elif previous["actual_spend"] == 0:
            result["formula"] = "Not computed: previous actual_spend is zero"
            result["status"] = "not_computed"
        else:
            result["formula"] = "(({} - {}) / {}) * 100".format(
                row["actual_spend"], previous["actual_spend"], previous["actual_spend"]
            )
            result["growth_percent"] = (
                (row["actual_spend"] - previous["actual_spend"])
                / previous["actual_spend"]
                * 100
            )
        results.append(result)
        previous = row
    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Calculate ward-category budget growth.")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv")
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", default="growth_output.csv")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        output_path = Path(args.output)
        with output_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(results)
    except (OSError, ValueError) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
