import argparse
import csv


NULL_VALUES = {"", "null", "none", "na", "n/a"}

REQUIRED_COLUMNS = {
    "ward",
    "category",
    "period",
    "budgeted_amount",
    "actual_spend",
    "notes",
}

GROWTH_FORMULA = (
    "(current actual_spend - previous actual_spend) "
    "/ previous actual_spend * 100"
)


def is_null(value):
    return str(value or "").strip().lower() in NULL_VALUES


def load_dataset(input_path):
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or []

            columns = {
                column.strip().lower()
                for column in fieldnames
                if column
            }

            missing = REQUIRED_COLUMNS - columns

            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}"
                )

            rows = list(reader)

    except FileNotFoundError:
        raise SystemExit(f"Input file not found: {input_path}")

    null_rows = []

    for row in rows:
        if is_null(row.get("actual_spend")):
            null_rows.append(
                {
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "period": row.get("period", ""),
                    "reason": row.get("notes", ""),
                }
            )

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Growth type must be MoM or YoY.")

    selected = [
        row
        for row in rows
        if row.get("ward") == ward
        and row.get("category") == category
    ]

    selected.sort(key=lambda row: row.get("period", ""))

    results = []

    for index, row in enumerate(selected):
        actual_text = str(
            row.get("actual_spend", "") or ""
        ).strip()

        if is_null(actual_text):
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row.get("period", ""),
                    "growth_type": growth_type,
                    "result": "FLAGGED_NULL",
                    "formula": (
                        "Not computed because current "
                        "actual_spend is NULL"
                    ),
                    "null_reason": row.get("notes", ""),
                }
            )
            continue

        previous_index = (
            index - 1 if growth_type == "MoM" else index - 12
        )

        if previous_index < 0:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row.get("period", ""),
                    "growth_type": growth_type,
                    "result": "N/A",
                    "formula": GROWTH_FORMULA,
                    "null_reason": "",
                }
            )
            continue

        previous_row = selected[previous_index]

        previous_text = str(
            previous_row.get("actual_spend", "") or ""
        ).strip()

        if is_null(previous_text):
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row.get("period", ""),
                    "growth_type": growth_type,
                    "result": "FLAGGED_NULL",
                    "formula": (
                        "Not computed because comparison "
                        "actual_spend is NULL"
                    ),
                    "null_reason": previous_row.get("notes", ""),
                }
            )
            continue

        try:
            current = float(actual_text)
            previous = float(previous_text)

            if previous == 0:
                result = "N/A"
            else:
                result = round(
                    (current - previous) / previous * 100,
                    1,
                )

        except ValueError:
            result = "N/A"

        results.append(
            {
                "ward": ward,
                "category": category,
                "period": row.get("period", ""),
                "growth_type": growth_type,
                "result": result,
                "formula": GROWTH_FORMULA,
                "null_reason": "",
            }
        )

    return results, selected


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY"],
    )
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    results, _ = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type,
    )

    fieldnames = [
        "ward",
        "category",
        "period",
        "growth_type",
        "result",
        "formula",
        "null_reason",
    ]

    with open(
        args.output,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Null rows found: {len(null_rows)}")
    print(f"Wrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()