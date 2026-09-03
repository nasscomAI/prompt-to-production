"""
UC-0C — Municipal Budget Growth Analyzer
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

VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(input_path: str):
    """Load and validate the budget CSV."""

    with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("Dataset has no header row.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing_columns))}"
            )

        rows = list(reader)

    null_rows = [
        row
        for row in rows
        if not (row.get("actual_spend") or "").strip()
    ]

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | {row.get('notes', '')}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for exactly one ward and one category."""

    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            "Invalid growth type. Specify exactly 'MoM' or 'YoY'."
        )

    matching_rows = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not matching_rows:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    matching_rows.sort(key=lambda row: row["period"])

    output = []

    for index, row in enumerate(matching_rows):
        actual_value = (row.get("actual_spend") or "").strip()

        # Null actual spend must always be flagged.
        if not actual_value:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "growth_type": growth_type,
                "previous_period": "",
                "previous_actual_spend": "",
                "formula": "",
                "growth_percent": "",
                "flag": "NULL actual_spend - not computed",
                "notes": row.get("notes", ""),
            })
            continue

        current = float(actual_value)

        previous_row = None

        if growth_type == "MoM":
            if index > 0:
                previous_row = matching_rows[index - 1]

        elif growth_type == "YoY":
            target_period = (
                f"{int(row['period'][:4]) - 1}{row['period'][4:]}"
            )

            for candidate in matching_rows:
                if candidate["period"] == target_period:
                    previous_row = candidate
                    break

        # First period has no previous period for growth.
        if previous_row is None:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": actual_value,
                "growth_type": growth_type,
                "previous_period": "",
                "previous_actual_spend": "",
                "formula": "",
                "growth_percent": "",
                "flag": "No previous period available - not computed",
                "notes": row.get("notes", ""),
            })
            continue

        previous_value = (previous_row.get("actual_spend") or "").strip()

        # Previous value is null, so growth cannot be calculated.
        if not previous_value:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": actual_value,
                "growth_type": growth_type,
                "previous_period": previous_row["period"],
                "previous_actual_spend": "",
                "formula": "",
                "growth_percent": "",
                "flag": "Previous actual_spend is NULL - not computed",
                "notes": row.get("notes", ""),
            })
            continue

        previous = float(previous_value)

        if previous == 0:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": actual_value,
                "growth_type": growth_type,
                "previous_period": previous_row["period"],
                "previous_actual_spend": previous_value,
                "formula": "",
                "growth_percent": "",
                "flag": "Previous actual_spend is zero - not computed",
                "notes": row.get("notes", ""),
            })
            continue

        growth = ((current - previous) / previous) * 100

        formula = (
            f"(({current:.1f} - {previous:.1f}) / "
            f"{previous:.1f}) * 100"
        )

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual_value,
            "growth_type": growth_type,
            "previous_period": previous_row["period"],
            "previous_actual_spend": previous_value,
            "formula": formula,
            "growth_percent": f"{growth:.1f}%",
            "flag": "",
            "notes": row.get("notes", ""),
        })

    return output


def write_output(output_path: str, rows):
    """Write growth results to CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "previous_period",
        "previous_actual_spend",
        "formula",
        "growth_percent",
        "flag",
        "notes",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate municipal budget growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward budget CSV.",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name.",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
        help="Growth calculation type.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Results written to {Path(args.output)}")


if __name__ == "__main__":
    main()