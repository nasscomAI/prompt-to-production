import argparse
import csv
import os
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    """Load and validate the ward budget CSV."""

    if not os.path.isfile(input_path):
        raise ValueError(f"Input file not found: {input_path}")

    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    "Missing required columns: " + ", ".join(sorted(missing))
                )

            rows = list(reader)

    except OSError as exc:
        raise ValueError(f"Could not read input file: {exc}") from exc

    if not rows:
        raise ValueError("CSV contains no data rows.")

    null_rows = []

    for row_number, row in enumerate(rows, start=2):
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append(
                {
                    "row": row_number,
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"],
                }
            )
        else:
            try:
                float(actual)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid actual_spend at CSV row {row_number}: {actual}"
                ) from exc

        try:
            float(row["budgeted_amount"])
        except ValueError as exc:
            raise ValueError(
                f"Invalid budgeted_amount at CSV row {row_number}: "
                f"{row['budgeted_amount']}"
            ) from exc

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward and one category."""

    if not growth_type:
        raise ValueError(
            "--growth-type is required. Refusing to guess the growth formula."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "This implementation supports MoM only."
        )

    selected = [
        row
        for row in rows
        if row["ward"].strip() == ward and row["category"].strip() == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    output = []
    previous_value = None
    previous_period = None

    for row in selected:
        period = row["period"].strip()
        actual_text = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual_text == "":
            output.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": "",
                    "formula": "NOT COMPUTED - actual_spend is NULL",
                    "growth": "",
                    "status": f"FLAGGED: {notes}",
                }
            )

            # A missing month cannot be used as the previous value
            # for the next month's MoM calculation.
            previous_value = None
            previous_period = None
            continue

        current_value = float(actual_text)

        if previous_value is None:
            formula = "NOT COMPUTED - no valid previous-period actual_spend"
            growth = ""
            status = "BASE PERIOD"
        else:
            growth_value = ((current_value - previous_value) / previous_value) * 100

            formula = (
                f"(({current_value:g} - {previous_value:g}) / "
                f"{previous_value:g}) * 100"
            )
            growth = f"{growth_value:+.1f}%"
            status = f"Compared with {previous_period}"

        output.append(
            {
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{current_value:g}",
                "formula": formula,
                "growth": growth,
                "status": status,
            }
        )

        previous_value = current_value
        previous_period = period

    return output


def write_output(output_path, results):
    """Write the growth results to CSV."""

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "ward",
            "category",
            "period",
            "actual_spend",
            "formula",
            "growth",
            "status",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate per-ward, per-category MoM budget growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the ward budget CSV.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type. Must be MoM.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        # Refuse wildcard/all-ward style requests.
        if args.ward.strip().lower() in {"all", "*", "any"}:
            raise ValueError(
                "Refusing all-ward aggregation. Specify exactly one ward."
            )

        if args.category.strip().lower() in {"all", "*", "any"}:
            raise ValueError(
                "Refusing cross-category aggregation. Specify exactly one category."
            )

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(args.output, results)

        print(f"Loaded {len(rows)} rows.")
        print(f"Found {len(null_rows)} NULL actual_spend rows in the dataset.")

        for item in null_rows:
            print(
                f"NULL: {item['period']} | "
                f"{item['ward']} | "
                f"{item['category']} | "
                f"Reason: {item['reason']}"
            )

        print(f"Results written to {args.output}")

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()