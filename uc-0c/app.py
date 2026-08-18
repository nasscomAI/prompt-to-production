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


def load_dataset(path):
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                "Input CSV is missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    null_rows = [
        row for row in rows
        if not row["actual_spend"].strip()
    ]

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"  {row['period']} | {row['ward']} | "
            f"{row['category']} | {row['notes']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    if not growth_type:
        raise ValueError(
            "growth_type is required. Specify MoM."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth_type: {growth_type}. "
            "This UC supports MoM only."
        )

    filtered = [
        row for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' "
            f"and category '{category}'."
        )

    filtered.sort(key=lambda row: row["period"])

    results = []
    previous_actual = None

    for row in filtered:
        actual_text = row["actual_spend"].strip()

        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual_text,
            "growth_type": growth_type,
            "growth_percent": "",
            "formula": "",
            "status": "",
            "note": "",
        }

        if not actual_text:
            result["status"] = "NULL_FLAGGED"
            result["note"] = row["notes"]
            result["formula"] = (
                "Not computed because actual_spend is NULL"
            )

            results.append(result)

            # A missing current value means we cannot use it
            # as the previous value for the next calculation.
            previous_actual = None
            continue

        current_actual = float(actual_text)

        if previous_actual is None:
            result["status"] = "BASELINE"
            result["formula"] = (
                "No previous valid period available for MoM"
            )
        else:
            growth = (
                (current_actual - previous_actual)
                / previous_actual
            ) * 100

            result["growth_percent"] = f"{growth:.1f}"
            result["status"] = "CALCULATED"
            result["formula"] = (
                f"(({current_actual:.1f} - "
                f"{previous_actual:.1f}) / "
                f"{previous_actual:.1f}) * 100"
            )

        results.append(result)
        previous_actual = current_actual

    return results


def write_output(path, rows):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_percent",
        "formula",
        "status",
        "note",
    ]

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C ward budget growth analysis"
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

    print(f"Growth output written to {args.output}")


if __name__ == "__main__":
    main()