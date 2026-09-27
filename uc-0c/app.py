from pathlib import Path
import argparse
import csv


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR.parent / "data" / "budget" / "ward_budget.csv"
DEFAULT_OUTPUT = BASE_DIR / "growth_output.csv"


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate ward/category growth from the budget dataset."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    return parser.parse_args()


def load_dataset(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV has no header.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )

        rows = list(reader)

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


def calculate_mom(rows, ward, category):
    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    selected.sort(key=lambda row: row["period"])

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    output = []

    previous_spend = None
    previous_period = None

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
                "status": "FLAGGED_NULL",
                "null_reason": row["notes"],
            })

            previous_spend = None
            previous_period = row["period"]
            continue

        current_spend = float(actual)

        if previous_spend is None:
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — no valid previous-period actual_spend",
                "growth": "",
                "status": "NO_BASELINE",
                "null_reason": "",
            })
        else:
            growth = ((current_spend - previous_spend) / previous_spend) * 100

            formula = (
                f"(({current_spend:.2f} - {previous_spend:.2f}) "
                f"/ {previous_spend:.2f}) × 100"
            )

            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": formula,
                "growth": f"{growth:+.1f}%",
                "status": "COMPUTED",
                "null_reason": "",
            })

        previous_spend = current_spend
        previous_period = row["period"]

    return output


def validate_request(ward, category, growth_type):
    if not ward.strip():
        raise ValueError("Ward is required.")

    if not category.strip():
        raise ValueError("Category is required.")

    if not growth_type.strip():
        raise ValueError(
            "Growth type was not specified. Refusing to guess."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            "Only explicitly requested MoM growth is supported by this use case."
        )

    if ward.lower() in {"all", "all wards", "all-ward"}:
        raise ValueError(
            "REFUSED: cross-ward aggregation is not permitted."
        )

    if category.lower() in {"all", "all categories", "all-category"}:
        raise ValueError(
            "REFUSED: cross-category aggregation is not permitted."
        )


def write_output(path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth",
        "status",
        "null_reason",
    ]

    with Path(path).open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()

    validate_request(
        args.ward,
        args.category,
        args.growth_type,
    )

    rows = load_dataset(args.input)

    result = calculate_mom(
        rows,
        args.ward,
        args.category,
    )

    write_output(args.output, result)

    print()
    print(f"Growth type: {args.growth_type}")
    print(f"Ward: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()