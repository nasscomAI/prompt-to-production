import argparse
import csv
import os


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_file):
    """Load and validate the budget CSV."""

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        rows = list(reader)

    null_rows = []

    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append(row)

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward and category."""

    if not growth_type:
        raise ValueError(
            "--growth-type must be specified. The growth formula cannot be guessed."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. Only MoM is supported."
        )

    # Refuse all-ward or cross-category aggregation.
    if ward.lower() in {"all", "all wards", "all-ward"}:
        raise ValueError("All-ward aggregation is not permitted.")

    filtered = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    filtered.sort(key=lambda row: row["period"])

    results = []
    previous_spend = None

    for row in filtered:
        period = row["period"]
        actual = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "formula": "NOT COMPUTED — actual_spend is NULL",
                "growth": "",
                "flag": f"NULL — {notes}",
            })

            previous_spend = None
            continue

        current_spend = float(actual)

        if previous_spend is None or previous_spend == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_spend,
                "formula": "NOT COMPUTED — no valid previous-month actual_spend",
                "growth": "",
                "flag": "",
            })
        else:
            growth = ((current_spend - previous_spend) / previous_spend) * 100

            formula = (
                f"(({current_spend:g} - {previous_spend:g}) "
                f"/ {previous_spend:g}) * 100"
            )

            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": current_spend,
                "formula": formula,
                "growth": f"{growth:+.1f}%",
                "flag": "",
            })

        previous_spend = current_spend

    return results


def write_output(output_file, results):
    """Write the calculated results to CSV."""

    output_dir = os.path.dirname(output_file)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth",
        "flag",
    ]

    with open(output_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ward-level month-over-month infrastructure spending growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the budget CSV file.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Ward to analyze.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Category to analyze.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output CSV file.",
    )

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    # Report all null rows before computation.
    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"Reason: {row['notes']}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Results written successfully: {args.output}")


if __name__ == "__main__":
    main()