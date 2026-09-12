"""
UC-0C — Ward/Category Growth Calculator

Computes growth at exactly one ward + one category level.
Null actual_spend values are flagged and never used in growth calculations.
"""

import argparse
import csv


def load_dataset(path):
    """Read CSV, validate required columns, and report null actual_spend rows."""
    required_columns = {
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "notes",
    }

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])

        missing = required_columns - columns
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        rows = list(reader)

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """
    Return per-period growth for one ward and one category.

    MoM formula:
    ((current_actual - previous_actual) / previous_actual) * 100

    A row with NULL actual_spend is flagged and not computed.
    A row whose previous period is NULL is also flagged and not computed.
    """

    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. This implementation requires --growth-type MoM."
        )

    selected = [
        row for row in rows
        if row["ward"].strip() == ward
        and row["category"].strip() == category
    ]

    selected.sort(key=lambda row: row["period"])

    results = []
    previous_actual = None
    previous_period = None

    for row in selected:
        period = row["period"].strip()
        actual_text = row["actual_spend"].strip()
        notes = row["notes"].strip()

        if actual_text == "":
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": "",
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "NOT COMPUTED — actual_spend is NULL",
                "flag": f"NULL ACTUAL_SPEND — {notes}",
            })
            previous_actual = None
            previous_period = period
            continue

        current_actual = float(actual_text)

        if previous_actual is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": current_actual,
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "NOT COMPUTED — no valid previous-period actual_spend",
                "flag": "FIRST VALID PERIOD OR PREVIOUS PERIOD WAS NULL",
            })
        elif previous_actual == 0:
            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": current_actual,
                "growth_type": growth_type,
                "growth_percent": "",
                "formula": "NOT COMPUTED — previous actual_spend is 0",
                "flag": "PREVIOUS ACTUAL_SPEND IS ZERO",
            })
        else:
            growth = ((current_actual - previous_actual) / previous_actual) * 100

            results.append({
                "ward": ward,
                "category": category,
                "period": period,
                "actual_spend": current_actual,
                "growth_type": growth_type,
                "growth_percent": round(growth, 1),
                "formula": (
                    f"(({current_actual:.1f} - {previous_actual:.1f}) "
                    f"/ {previous_actual:.1f}) * 100"
                ),
                "flag": "",
            })

        previous_actual = current_actual
        previous_period = period

    return results


def write_output(path, results):
    """Write the growth table to CSV."""
    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "flag",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    # Refuse to guess the growth method.
    if not args.growth_type:
        raise ValueError(
            "ERROR: --growth-type is required. Refusing to guess the formula."
        )

    # Refuse an all-ward/all-category aggregation request.
    if args.ward.strip().lower() in {"all", "all wards", "all-wards"}:
        raise ValueError(
            "REFUSED: aggregation across wards is not allowed."
        )

    if args.category.strip().lower() in {"all", "all categories", "all-categories"}:
        raise ValueError(
            "REFUSED: aggregation across categories is not allowed."
        )

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} NULL actual_spend rows.")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | reason: {row['notes']}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    if not results:
        raise ValueError(
            f"No rows found for ward '{args.ward}' "
            f"and category '{args.category}'."
        )

    write_output(args.output, results)

    print(f"Wrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()