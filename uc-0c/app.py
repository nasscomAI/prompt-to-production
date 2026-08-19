import argparse
import csv
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

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
    print(f"Found {len(null_rows)} null actual_spend values.")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | Reason: {row['notes'] or 'No reason provided'}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError(
            "Growth type is required. Specify --growth-type, for example MoM."
        )

    if growth_type != "MoM":
        raise ValueError(
            "Unsupported growth type. Only MoM is supported."
        )

    selected = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    output = []

    previous = None

    for row in selected:
        current = row["actual_spend"]

        if current.strip() == "":
            output.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "growth": "NULL",
                "formula": "NOT COMPUTED",
                "status": "NULL - " + (
                    row["notes"] or "No reason provided"
                ),
            })
            previous = None
            continue

        current_value = float(current)

        if previous is None:
            output.append({
                "period": row["period"],
                "ward": ward,
                "category": category,
                "actual_spend": current_value,
                "growth": "N/A",
                "formula": "N/A - first month or previous value unavailable",
                "status": "OK",
            })
        else:
            previous_value = previous["value"]

            if previous_value == 0:
                output.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_value,
                    "growth": "N/A",
                    "formula": "NOT COMPUTED - previous value is zero",
                    "status": "Cannot divide by zero",
                })
            else:
                growth = (
                    (current_value - previous_value)
                    / previous_value
                ) * 100

                formula = (
                    f"(({current_value:.1f} - {previous_value:.1f}) "
                    f"/ {previous_value:.1f}) * 100"
                )

                output.append({
                    "period": row["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": current_value,
                    "growth": f"{growth:.1f}%",
                    "formula": formula,
                    "status": "OK",
                })

        previous = {
            "value": current_value,
            "period": row["period"],
        }

    return output


def write_output(path, results):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth",
        "formula",
        "status",
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate per-ward, per-category budget growth."
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(args.output, results)

        print(f"Growth analysis written to {args.output}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()