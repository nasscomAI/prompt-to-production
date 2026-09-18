"""
UC-0C - Number That Looks Right

Deterministic implementation for transparent per-ward, per-category
month-over-month growth calculation.
"""

import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

ALLOWED_GROWTH_TYPES = {"MoM"}


def load_dataset(input_path: str):
    """Load and validate the ward budget CSV."""
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Dataset has no header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Dataset is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    null_rows = [row for row in rows if row["actual_spend"].strip() == ""]

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes']}"
        )

    return rows


def validate_request(rows, ward, category, growth_type):
    """Validate the requested ward, category, and growth type."""
    if not growth_type:
        raise ValueError(
            "--growth-type is required. "
            "The growth formula must be explicitly specified."
        )

    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth type: {growth_type}. " f"Supported value: MoM"
        )

    if ward is None or not ward.strip():
        raise ValueError("A specific ward must be provided.")

    if category is None or not category.strip():
        raise ValueError("A specific category must be provided.")

    if ward.strip().lower() in {"all", "all wards", "any"}:
        raise ValueError("All-ward aggregation is not permitted. " "Specify one ward.")

    if category.strip().lower() in {"all", "all categories", "any"}:
        raise ValueError(
            "Cross-category aggregation is not permitted. " "Specify one category."
        )

    available_wards = {row["ward"] for row in rows}
    available_categories = {row["category"] for row in rows}

    if ward not in available_wards:
        raise ValueError(f"Ward not found in dataset: {ward}")

    if category not in available_categories:
        raise ValueError(f"Category not found in dataset: {category}")


def compute_mom(rows, ward, category):
    """
    Compute monthly MoM growth for one ward and one category.

    Formula:
        ((current actual_spend - previous actual_spend)
         / previous actual_spend) * 100
    """
    selected = [
        row for row in rows if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    if not selected:
        raise ValueError(f"No data found for ward '{ward}' and category '{category}'.")

    results = []
    previous_spend = None
    previous_period = None

    formula = (
        "((current actual_spend - previous actual_spend) "
        "/ previous actual_spend) * 100"
    )

    for row in selected:
        current_raw = row["actual_spend"].strip()

        if current_raw == "":
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": "",
                    "previous_period": previous_period or "",
                    "previous_actual_spend": (
                        "" if previous_spend is None else previous_spend
                    ),
                    "growth_type": "MoM",
                    "formula": formula,
                    "growth_percent": "",
                    "status": "FLAGGED_NULL",
                    "null_reason": row["notes"],
                }
            )

            # A missing current value cannot become the baseline for
            # the next month's growth calculation.
            previous_spend = None
            previous_period = row["period"]
            continue

        current_spend = float(current_raw)

        if previous_spend is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current_spend,
                    "previous_period": previous_period or "",
                    "previous_actual_spend": "",
                    "growth_type": "MoM",
                    "formula": formula,
                    "growth_percent": "",
                    "status": "NO_PREVIOUS_PERIOD",
                    "null_reason": "",
                }
            )
        else:
            growth = ((current_spend - previous_spend) / previous_spend) * 100

            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current_spend,
                    "previous_period": previous_period,
                    "previous_actual_spend": previous_spend,
                    "growth_type": "MoM",
                    "formula": formula,
                    "growth_percent": round(growth, 1),
                    "status": "COMPUTED",
                    "null_reason": "",
                }
            )

        previous_spend = current_spend
        previous_period = row["period"]

    return results


def write_output(output_path: str, results):
    """Write the growth results to CSV."""
    path = Path(output_path)

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "previous_period",
        "previous_actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "null_reason",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Specific ward to analyze",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Specific category to analyze",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type. Supported value: MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    validate_request(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    results = compute_mom(
        rows,
        args.ward,
        args.category,
    )

    write_output(args.output, results)

    print(f"Growth results written to {args.output}")


if __name__ == "__main__":
    main()
