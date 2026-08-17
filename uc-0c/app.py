import argparse
import csv
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

VALID_GROWTH_TYPES = {"MoM"}


def load_dataset(input_path):
    """Load and validate the ward budget dataset."""

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as infile:
            reader = csv.DictReader(infile)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header.")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)

            if missing:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(sorted(missing))
                )

            rows = list(reader)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input CSV was not found: {input_path}"
        )

    null_rows = []

    for row in rows:
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"].strip(),
            })
        else:
            try:
                float(actual)
            except ValueError:
                raise ValueError(
                    f"Invalid actual_spend value "
                    f"for {row['period']} / "
                    f"{row['ward']} / "
                    f"{row['category']}: {actual}"
                )

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """
    Compute growth for exactly one ward and one category.

    Currently supports only explicitly requested MoM growth.
    """

    if not ward:
        raise ValueError(
            "Ward must be explicitly specified."
        )

    if not category:
        raise ValueError(
            "Category must be explicitly specified."
        )

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly specified."
        )

    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "This implementation supports only MoM."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' "
            f"and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:
        period = row["period"]
        actual_text = row["actual_spend"].strip()

        # Current actual spend is missing.
        if actual_text == "":
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "",
                "formula": "NOT COMPUTED - actual_spend is NULL",
                "growth": "",
                "status": "FLAGGED_NULL",
                "reason": row["notes"].strip(),
            })

            # A null current value cannot become the previous
            # value for the next calculation.
            previous_actual = None
            previous_period = period
            continue

        current_actual = float(actual_text)

        # No previous period exists.
        if previous_actual is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": f"{current_actual:.2f}",
                "formula": "NOT COMPUTED - no previous-period actual_spend",
                "growth": "",
                "status": "NOT_COMPUTED",
                "reason": (
                    "MoM growth requires a previous-period "
                    "actual_spend value."
                ),
            })
        else:
            formula = (
                f"(({current_actual:.2f} - "
                f"{previous_actual:.2f}) / "
                f"{previous_actual:.2f}) * 100"
            )

            if previous_actual == 0:
                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": f"{current_actual:.2f}",
                    "formula": formula,
                    "growth": "",
                    "status": "NOT_COMPUTED",
                    "reason": (
                        "Previous-period actual_spend is zero; "
                        "MoM percentage growth is undefined."
                    ),
                })
            else:
                growth = (
                    (current_actual - previous_actual)
                    / previous_actual
                    * 100
                )

                results.append({
                    "ward": ward,
                    "category": category,
                    "period": period,
                    "actual_spend": f"{current_actual:.2f}",
                    "formula": formula,
                    "growth": f"{growth:.1f}%",
                    "status": "COMPUTED",
                    "reason": "",
                })

        previous_actual = current_actual
        previous_period = period

    return results


def write_output(output_path, results):
    """Write the per-period growth table."""

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "reason",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C ward budget growth analysis"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Explicit growth type, currently MoM"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path"
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(
            args.output,
            results
        )

        print(
            f"Done. Growth results written to {args.output}"
        )

        print(
            f"Dataset rows loaded: {len(rows)}"
        )

        print(
            f"Null actual_spend rows found: {len(null_rows)}"
        )

        for item in null_rows:
            print(
                "NULL:",
                item["period"],
                "|",
                item["ward"],
                "|",
                item["category"],
                "|",
                item["reason"],
            )

    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()