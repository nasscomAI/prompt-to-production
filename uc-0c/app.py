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


def load_dataset(input_path):
    path = Path(input_path)

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("Dataset is empty.")

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | reason: {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. This implementation requires MoM."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    output = []
    previous_value = None

    for row in selected:
        actual = row["actual_spend"].strip()

        if actual == "":
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — actual_spend is NULL",
                "growth": "",
                "null_reason": row["notes"],
            })
            previous_value = None
            continue

        current = float(actual)

        if previous_value is None:
            formula = "NOT COMPUTED — no valid previous month"
            growth = ""
        else:
            formula = (
                f"(({current:.2f} - {previous_value:.2f}) "
                f"/ {previous_value:.2f}) * 100"
            )
            growth = round(
                ((current - previous_value) / previous_value) * 100,
                1,
            )

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": current,
            "growth_type": "MoM",
            "formula": formula,
            "growth": growth,
            "null_reason": "",
        })

        previous_value = current

    return output


def write_output(output_path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "null_reason",
    ]

    with Path(output_path).open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C ward/category growth calculator"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows = load_dataset(args.input)

    # Refuse ambiguous aggregation.
    if args.ward.lower() in {"all", "all wards", "*"}:
        raise ValueError(
            "REFUSED: all-ward aggregation is not permitted."
        )

    if args.category.lower() in {"all", "all categories", "*"}:
        raise ValueError(
            "REFUSED: all-category aggregation is not permitted."
        )

    result = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, result)

    print(f"Done. Wrote {len(result)} rows to {args.output}")


if __name__ == "__main__":
    main()