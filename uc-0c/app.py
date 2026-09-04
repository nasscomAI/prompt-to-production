"""
UC-0C — Number That Looks Right

Per-ward, per-category growth calculator.
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
    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("CSV has no header.")

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(missing)
            )

        rows = list(reader)

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    print(f"Loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} NULL actual_spend rows.")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError(
            "--growth-type is required. Use MoM or YoY."
        )

    growth_type = growth_type.upper()

    if growth_type not in {"MOM", "YOY"}:
        raise ValueError(
            "Invalid growth type. Use MoM or YoY."
        )

    if ward.lower() in {"all", "all wards", "*"}:
        raise ValueError(
            "Refusing all-ward aggregation. Specify one ward."
        )

    if category.lower() in {"all", "all categories", "*"}:
        raise ValueError(
            "Refusing all-category aggregation. Specify one category."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            "No data found for the requested ward and category."
        )

    selected.sort(key=lambda row: row["period"])

    values = {
        row["period"]: row["actual_spend"].strip()
        for row in selected
    }

    results = []

    for index, row in enumerate(selected):
        current = row["actual_spend"].strip()

        if not current:
            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "formula": "NOT COMPUTED — current actual_spend is NULL",
                "growth": "",
                "status": "FLAGGED NULL",
                "null_reason": row["notes"],
            })
            continue

        if growth_type == "MOM":
            if index == 0:
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": current,
                    "formula": "N/A — first period has no previous month",
                    "growth": "",
                    "status": "NO BASELINE",
                    "null_reason": "",
                })
                continue

            previous_row = selected[index - 1]
            previous = previous_row["actual_spend"].strip()

            if not previous:
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": current,
                    "formula": (
                        "NOT COMPUTED — previous month "
                        f"{previous_row['period']} actual_spend is NULL"
                    ),
                    "growth": "",
                    "status": "FLAGGED NULL BASELINE",
                    "null_reason": previous_row["notes"],
                })
                continue

            previous_value = float(previous)
            current_value = float(current)

            if previous_value == 0:
                raise ValueError(
                    f"Cannot calculate growth for {row['period']}: "
                    "previous actual_spend is zero."
                )

            growth = (
                (current_value - previous_value)
                / previous_value
            ) * 100

            formula = (
                f"(({current_value} - {previous_value}) "
                f"/ {previous_value}) * 100"
            )

        else:
            # YoY requires the same month in the previous year.
            year = int(row["period"][:4])
            month = row["period"][5:]
            previous_period = f"{year - 1}-{month}"

            previous = values.get(previous_period, "")

            if not previous:
                results.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "actual_spend": current,
                    "formula": (
                        f"NOT COMPUTED — {previous_period} "
                        "actual_spend is unavailable"
                    ),
                    "growth": "",
                    "status": "NO YOY BASELINE",
                    "null_reason": "",
                })
                continue

            previous_value = float(previous)
            current_value = float(current)

            if previous_value == 0:
                raise ValueError(
                    f"Cannot calculate growth for {row['period']}: "
                    "previous-year actual_spend is zero."
                )

            growth = (
                (current_value - previous_value)
                / previous_value
            ) * 100

            formula = (
                f"(({current_value} - {previous_value}) "
                f"/ {previous_value}) * 100"
            )

        results.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current,
            "formula": formula,
            "growth": f"{growth:.1f}%",
            "status": "CALCULATED",
            "null_reason": "",
        })

    return results


def write_output(output_path, results):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
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
        description="UC-0C per-ward, per-category growth calculator"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input)

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Growth results written to {args.output}")


if __name__ == "__main__":
    main()