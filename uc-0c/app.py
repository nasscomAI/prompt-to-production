""""
UC-0C — Budget Growth Calculator

Rules:
- One ward + one category at a time.
- growth_type is mandatory.
- Null actual_spend values are never replaced or guessed.
- Every computed row shows its formula.
- MoM is the supported growth calculation.
"""

import argparse
import csv


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    """
    Load and validate the budget CSV.

    Returns:
        list[dict]: Dataset rows.

    Raises:
        ValueError: If required columns are missing.
    """

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = [
        row
        for row in rows
        if row.get("actual_spend", "").strip() == ""
    ]

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | "
            f"{row['ward']} | "
            f"{row['category']} | "
            f"Reason: {row.get('notes', '')}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """
    Compute growth for exactly one ward and one category.

    Currently supports MoM only.
    """

    if not growth_type:
        raise ValueError(
            "growth_type is required. Specify --growth-type MoM."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "This implementation supports only MoM."
        )

    if not ward or not category:
        raise ValueError(
            "Both --ward and --category are required."
        )

    # Refuse accidental aggregation.
    if ward.lower() in {"all", "all wards", "*"}:
        raise ValueError(
            "Refusing all-ward aggregation. Specify exactly one ward."
        )

    if category.lower() in {"all", "all categories", "*"}:
        raise ValueError(
            "Refusing all-category aggregation. Specify exactly one category."
        )

    selected = [
        row
        for row in rows
        if row["ward"] == ward
        and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No rows found for ward '{ward}' "
            f"and category '{category}'."
        )

    # Dataset periods are YYYY-MM, so string sorting is chronological.
    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:
        current_raw = row["actual_spend"].strip()

        if current_raw == "":
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": "",
                    "growth_type": growth_type,
                    "formula": "NOT COMPUTED — current actual_spend is NULL",
                    "growth": "",
                    "status": "NEEDS_REVIEW",
                    "null_reason": row.get("notes", ""),
                }
            )

            previous_actual = None
            previous_period = row["period"]
            continue

        current_actual = float(current_raw)

        if previous_actual is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current_actual,
                    "growth_type": growth_type,
                    "formula": (
                        "NOT COMPUTED — no previous non-null "
                        "actual_spend available"
                    ),
                    "growth": "",
                    "status": "NO_BASELINE",
                    "null_reason": "",
                }
            )
        else:
            growth = (
                (current_actual - previous_actual)
                / previous_actual
            ) * 100

            formula = (
                f"(({current_actual:.1f} - {previous_actual:.1f}) "
                f"/ {previous_actual:.1f}) * 100"
            )

            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current_actual,
                    "growth_type": growth_type,
                    "formula": formula,
                    "growth": f"{growth:+.1f}%",
                    "status": "OK",
                    "null_reason": "",
                }
            )

        previous_actual = current_actual
        previous_period = row["period"]

    return results


def write_output(results, output_path):
    """Write the per-period growth table to CSV."""

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as outfile:
        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exactly one ward to analyze",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exactly one category to analyze",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type. Currently: MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(results, args.output)

    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
