import argparse
import csv


REQUIRED_COLUMNS = [
    "ward",
    "category",
    "period",
    "actual_spend",
    "notes",
]


def load_dataset(input_path):
    """Load CSV, validate columns, and report null rows."""
    with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]

    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    null_rows = []

    for row in rows:
        if not row["actual_spend"].strip():
            null_rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row["notes"],
            })

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward/category using the requested growth type."""

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Use --growth-type MoM or --growth-type YoY."
        )

    growth_type = growth_type.upper()

    if growth_type not in ("MOM", "YOY"):
        raise ValueError("growth_type must be either MoM or YoY.")

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    results = []

    for index, current in enumerate(selected):
        current_spend = current["actual_spend"].strip()

        if not current_spend:
            results.append({
                "period": current["period"],
                "ward": ward,
                "category": category,
                "growth": "",
                "formula": "NOT COMPUTED",
                "status": f"NULL - {current['notes']}",
            })
            continue

        current_value = float(current_spend)

        previous = None

        if growth_type == "MOM" and index > 0:
            previous = selected[index - 1]
        elif growth_type == "YOY" and index >= 12:
            previous = selected[index - 12]

        if previous is None or not previous["actual_spend"].strip():
            results.append({
                "period": current["period"],
                "ward": ward,
                "category": category,
                "growth": "",
                "formula": "NOT COMPUTED",
                "status": "Insufficient previous-period data",
            })
            continue

        previous_value = float(previous["actual_spend"])

        if previous_value == 0:
            results.append({
                "period": current["period"],
                "ward": ward,
                "category": category,
                "growth": "",
                "formula": "NOT COMPUTED",
                "status": "Previous value is zero",
            })
            continue

        growth = ((current_value - previous_value) / previous_value) * 100

        formula = (
            f"(({current_value} - {previous_value}) / "
            f"{previous_value}) * 100 = {growth:.1f}%"
        )

        results.append({
            "period": current["period"],
            "ward": ward,
            "category": category,
            "growth": f"{growth:.1f}%",
            "formula": formula,
            "status": "OK",
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Municipal Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the budget CSV"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to growth output CSV"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Ward to analyse"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Category to analyse"
    )

    parser.add_argument(
        "--growth-type",
        required=False,
        choices=["MoM", "YoY", "mom", "yoy"],
        help="Growth calculation type: MoM or YoY"
    )

    args = parser.parse_args()

    if not args.growth_type:
        raise SystemExit(
            "REFUSED: --growth-type is required. "
            "Specify MoM or YoY; the system will not guess."
        )

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for null_row in null_rows:
        print(
            f"NULL: {null_row['period']} | "
            f"{null_row['ward']} | "
            f"{null_row['category']} | "
            f"{null_row['reason']}"
        )

    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    with open(args.output, "w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "period",
            "ward",
            "category",
            "growth",
            "formula",
            "status",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Growth results written to {args.output}")


if __name__ == "__main__":
    main()