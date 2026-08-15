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


def load_dataset(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        rows = list(reader)

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Please provide --growth-type."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            "This task supports MoM growth only."
        )

    selected = []

    for row in rows:
        if (
            row["ward"].strip().replace("–", "-")
            == ward.strip().replace("–", "-")
            and row["category"].strip() == category.strip()
        ):
            selected.append(row)
    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []
    previous_spend = None

    for row in selected:

        value = row["actual_spend"].strip()

        # Handle NULL actual spend
        if value == "":
            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": "NOT COMPUTED - actual_spend is NULL",
                "growth": "",
                "flag": "NULL - " + row["notes"],
            })

            previous_spend = None
            continue

        current_spend = float(value)

        # First valid month
        if previous_spend is None:
            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": "NOT COMPUTED - no previous valid month",
                "growth": "",
                "flag": "",
            })

        else:
            growth = (
                (current_spend - previous_spend)
                / previous_spend
            ) * 100

            results.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": (
                    f"(({current_spend} - {previous_spend}) "
                    f"/ {previous_spend}) * 100"
                ),
                "growth": f"{growth:.1f}%",
                "flag": "",
            })

        previous_spend = current_spend

    return results


def write_output(path, results):

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "flag",
    ]

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)


def main():

    parser = argparse.ArgumentParser()

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
        args.growth_type
    )

    write_output(
        args.output,
        results
    )

    print(
        f"Done. {len(results)} rows written to "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()