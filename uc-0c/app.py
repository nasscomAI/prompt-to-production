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

VALID_GROWTH_TYPES = {"MoM"}


def load_dataset(input_path):
    """Load and validate the budget dataset."""
    with open(input_path, "r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("Input dataset is empty.")

    missing_columns = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing_columns))
        )

    null_rows = []

    for row in rows:
        if row["actual_spend"].strip() == "":
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"].strip() or "No reason provided",
                }
            )

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Return per-period growth for one ward/category combination."""

    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            "Unsupported growth type. This implementation supports MoM only."
        )

    if not ward or not category:
        raise ValueError("Ward and category must be explicitly specified.")

    if ward.strip().lower() in {"all", "all wards", "all-ward"}:
        raise ValueError(
            "Refusing all-ward aggregation. Specify one ward."
        )

    filtered = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    filtered.sort(key=lambda row: row["period"])

    output = []

    previous_row = None

    for row in filtered:
        current_value = row["actual_spend"].strip()

        if current_value == "":
            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": (
                        previous_row["actual_spend"].strip()
                        if previous_row
                        else ""
                    ),
                    "actual_spend": "",
                    "formula": "NOT COMPUTED — current actual_spend is NULL",
                    "growth": "",
                    "status": "FLAGGED_NULL",
                    "null_reason": row["notes"].strip()
                    or "No reason provided",
                }
            )
            previous_row = row
            continue

        if previous_row is None:
            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": "",
                    "actual_spend": current_value,
                    "formula": "NOT COMPUTED — no previous month",
                    "growth": "",
                    "status": "BASELINE",
                    "null_reason": "",
                }
            )
            previous_row = row
            continue

        previous_value = previous_row["actual_spend"].strip()

        if previous_value == "":
            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": "",
                    "actual_spend": current_value,
                    "formula": "NOT COMPUTED — previous actual_spend is NULL",
                    "growth": "",
                    "status": "FLAGGED_NULL",
                    "null_reason": (
                        previous_row["notes"].strip()
                        or "No reason provided"
                    ),
                }
            )
            previous_row = row
            continue

        current = float(current_value)
        previous = float(previous_value)

        if previous == 0:
            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": previous_value,
                    "actual_spend": current_value,
                    "formula": "NOT COMPUTED — previous actual_spend is 0",
                    "growth": "",
                    "status": "FLAGGED_ZERO_BASE",
                    "null_reason": "",
                }
            )
        else:
            growth = ((current - previous) / previous) * 100

            output.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": previous_value,
                    "actual_spend": current_value,
                    "formula": (
                        f"(({current_value} - {previous_value}) "
                        f"/ {previous_value}) × 100"
                    ),
                    "growth": f"{growth:.1f}%",
                    "status": "CALCULATED",
                    "null_reason": "",
                }
            )

        previous_row = row

    return output


def write_output(output_path, results):
    """Write the per-period growth table to CSV."""
    fieldnames = [
        "period",
        "ward",
        "category",
        "previous_actual_spend",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate per-period budget growth."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            "Growth type must be explicitly specified as MoM."
        )

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Found {len(null_rows)} null actual_spend rows.")

    for item in null_rows:
        print(
            f"NULL: {item['period']} | {item['ward']} | "
            f"{item['category']} | {item['reason']}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Growth table written to {args.output}")


if __name__ == "__main__":
    main()
