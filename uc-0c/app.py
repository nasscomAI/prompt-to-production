"""
UC-0C — Municipal Budget Variance Analyzer
"""

import argparse
import csv


REQUIRED_FIELDS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

# A record is considered significant when actual spending is at least
# 10% above the budgeted amount.
SIGNIFICANT_OVERRUN_PERCENT = 10.0


def parse_amount(value):
    """Convert a CSV amount to float, returning None when missing."""
    value = (value or "").strip()

    if not value:
        return None

    return float(value)


def analyze_row(row):
    """Analyze one budget row without inventing missing values."""

    budgeted = parse_amount(row.get("budgeted_amount"))
    actual = parse_amount(row.get("actual_spend"))

    if budgeted is None:
        return {
            "status": "INVALID",
            "variance": None,
            "variance_percent": None,
        }

    if actual is None:
        return {
            "status": "MISSING_ACTUAL",
            "variance": None,
            "variance_percent": None,
        }

    variance = actual - budgeted

    if budgeted == 0:
        variance_percent = None
    else:
        variance_percent = (variance / budgeted) * 100

    return {
        "status": "OK",
        "variance": variance,
        "variance_percent": variance_percent,
    }


def format_amount(value):
    """Format a numeric amount consistently."""
    return f"{value:.2f}"


def batch_budget_analysis(input_path, output_path):
    """Read the complete budget CSV and write an analysis report."""

    rows = []
    invalid_rows = []
    missing_actual_rows = []

    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        missing_fields = REQUIRED_FIELDS - set(reader.fieldnames)

        if missing_fields:
            raise ValueError(
                "Input CSV is missing required fields: "
                + ", ".join(sorted(missing_fields))
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                result = analyze_row(row)
            except (TypeError, ValueError):
                result = {
                    "status": "INVALID",
                    "variance": None,
                    "variance_percent": None,
                }

            record = {
                "row_number": row_number,
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": row.get("budgeted_amount", "").strip(),
                "actual_spend": row.get("actual_spend", "").strip(),
                "notes": row.get("notes", "").strip(),
                **result,
            }

            rows.append(record)

            if result["status"] == "INVALID":
                invalid_rows.append(record)
            elif result["status"] == "MISSING_ACTUAL":
                missing_actual_rows.append(record)

    overspending = [
        row
        for row in rows
        if row["status"] == "OK"
        and row["variance"] > 0
    ]

    significant_overspending = [
        row
        for row in rows
        if row["status"] == "OK"
        and row["variance_percent"] is not None
        and row["variance_percent"] >= SIGNIFICANT_OVERRUN_PERCENT
    ]

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("Municipal Budget Variance Analysis\n")
        outfile.write("=" * 40 + "\n\n")

        outfile.write(f"Total records: {len(rows)}\n")
        outfile.write(f"Valid records: {sum(r['status'] == 'OK' for r in rows)}\n")
        outfile.write(
            f"Missing actual-spend records: {len(missing_actual_rows)}\n"
        )
        outfile.write(f"Invalid records: {len(invalid_rows)}\n\n")

        outfile.write("SIGNIFICANT OVERSPENDING\n")
        outfile.write("-" * 40 + "\n")

        if significant_overspending:
            for row in significant_overspending:
                outfile.write(
                    f"{row['period']} | {row['ward']} | {row['category']} | "
                    f"Budget: {format_amount(float(row['budgeted_amount']))} | "
                    f"Actual: {format_amount(float(row['actual_spend']))} | "
                    f"Variance: {format_amount(row['variance'])} | "
                    f"Variance %: {row['variance_percent']:.2f}%\n"
                )
        else:
            outfile.write("No significant overspending records found.\n")

        outfile.write("\nMISSING ACTUAL SPEND\n")
        outfile.write("-" * 40 + "\n")

        if missing_actual_rows:
            for row in missing_actual_rows:
                note = row["notes"] or "No note supplied."
                outfile.write(
                    f"{row['period']} | {row['ward']} | {row['category']} | "
                    f"Budget: {row['budgeted_amount']} | "
                    f"Actual: MISSING | Notes: {note}\n"
                )
        else:
            outfile.write("No missing actual-spend records found.\n")

        outfile.write("\nALL VALID VARIANCES\n")
        outfile.write("-" * 40 + "\n")

        for row in rows:
            if row["status"] != "OK":
                continue

            outfile.write(
                f"{row['period']} | {row['ward']} | {row['category']} | "
                f"Budget: {format_amount(float(row['budgeted_amount']))} | "
                f"Actual: {format_amount(float(row['actual_spend']))} | "
                f"Variance: {format_amount(row['variance'])} | "
                f"Variance %: {row['variance_percent']:.2f}%\n"
            )

        if invalid_rows:
            outfile.write("\nINVALID RECORDS\n")
            outfile.write("-" * 40 + "\n")

            for row in invalid_rows:
                outfile.write(
                    f"CSV row {row['row_number']} | "
                    f"{row['period']} | {row['ward']} | "
                    f"{row['category']}\n"
                )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Municipal Budget Variance Analyzer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the budget CSV",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output report",
    )

    args = parser.parse_args()

    batch_budget_analysis(args.input, args.output)

    print(f"Done. Report written to {args.output}")


if __name__ == "__main__":
    main()