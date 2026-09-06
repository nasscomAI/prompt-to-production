import argparse
import csv
import re

REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def normalize_text(value):
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def load_dataset(input_csv):
    try:
        with open(input_csv, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_csv}")

    if not rows:
        raise ValueError("The input CSV is empty.")

    missing = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(sorted(missing))
        )

    null_rows = [
        row for row in rows
        if row["actual_spend"].strip() == ""
    ]

    print(f"Total NULL actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not ward or normalize_text(ward) in ("all", "any"):
        raise ValueError(
            "Refused: a single ward is required. All-ward aggregation is not allowed."
        )

    if not category or normalize_text(category) in ("all", "any"):
        raise ValueError(
            "Refused: a single category is required. Cross-category aggregation is not allowed."
        )

    if not growth_type:
        raise ValueError(
            "Growth type was not specified. Refusing to guess the formula."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. Only MoM is supported."
        )

    target_ward = normalize_text(ward)
    target_category = normalize_text(category)

    selected = [
        row for row in rows
        if normalize_text(row["ward"]) == target_ward
        and normalize_text(row["category"]) == target_category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    output = []
    previous_actual = None
    previous_period = None

    for row in selected:
        actual_text = row["actual_spend"].strip()

        if actual_text == "":
            output.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "",
                "mom_growth": "",
                "formula": (
                    f"Not computed: {row['period']} actual_spend is NULL; "
                    f"MoM formula not applied."
                ),
                "null_reason": row["notes"],
            })

            previous_actual = None
            previous_period = row["period"]
            continue

        current_actual = float(actual_text)

        if previous_actual is None:
            growth = ""
            formula = (
                f"Not computed: no previous valid actual_spend "
                f"before {row['period']}."
            )
        else:
            growth = (
                (current_actual - previous_actual)
                / previous_actual
                * 100
            )
            formula = (
                f"(({current_actual} - {previous_actual}) "
                f"/ {previous_actual}) * 100"
            )

        output.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual_text,
            "mom_growth": f"{growth:.1f}" if growth != "" else "",
            "formula": formula,
            "null_reason": "",
        })

        previous_actual = current_actual
        previous_period = row["period"]

    return output


def write_output(output, output_csv):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "mom_growth",
        "formula",
        "null_reason",
    ]

    with open(output_csv, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Number That Looks Right"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)

        result = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(result, args.output)

        print(f"Success: wrote {len(result)} rows to {args.output}")

    except ValueError as error:
        print(f"ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
