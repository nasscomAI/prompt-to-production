"""
UC-0C Budget Growth Analyzer

Calculates growth for one specified ward and category.
"""

import argparse
import csv


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(input_path):
    with open(input_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")

        missing = [
            column for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(missing)}"
            )

        rows = list(reader)

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Growth type is required. Do not guess it.")

    growth_type = growth_type.strip()

    if growth_type not in ["MoM"]:
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "Currently supported: MoM"
        )

    selected = [
        row for row in rows
        if row["ward"].strip() == ward.strip()
        and row["category"].strip() == category.strip()
    ]

    if not selected:
        raise ValueError(
            "No data found for the specified ward and category."
        )

    selected.sort(key=lambda row: row["period"])

    results = []
    previous_actual = None

    for row in selected:
        actual_text = (row["actual_spend"] or "").strip()
        notes = (row["notes"] or "").strip()

        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"],
            "notes": notes,
        }

        if not actual_text:
            result["notes"] = (
                f"{notes} Missing actual_spend; growth not calculated."
            ).strip()
            results.append(result)

            previous_actual = None
            continue

        try:
            actual = float(actual_text)
        except ValueError:
            result["notes"] = (
                f"{notes} Invalid actual_spend; growth not calculated."
            ).strip()
            results.append(result)

            previous_actual = None
            continue

        if previous_actual is None:
            result["notes"] = (
                f"{notes} No previous period actual_spend available; "
                "MoM growth not calculated."
            ).strip()
        else:
            if previous_actual == 0:
                result["notes"] = (
                    f"{notes} Previous actual_spend was 0; "
                    "MoM growth cannot be calculated."
                ).strip()
            else:
                growth = (
                    (actual - previous_actual)
                    / previous_actual
                ) * 100

                formula = (
                    f"({actual:.1f} - {previous_actual:.1f}) "
                    f"/ {previous_actual:.1f} × 100 = {growth:.1f}%"
                )

                result["notes"] = (
                    f"{notes} Formula: {formula}"
                ).strip()

        results.append(result)
        previous_actual = actual

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Calculate budget growth for one ward and category."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to budget CSV.",
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
        help="Growth type, currently MoM.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path.",
    )

    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        output_fields = [
            "period",
            "ward",
            "category",
            "budgeted_amount",
            "actual_spend",
            "notes",
        ]

        with open(
            args.output,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=output_fields,
            )
            writer.writeheader()
            writer.writerows(results)

        print(
            f"Growth calculation complete. Written to {args.output}"
        )

    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()