"""
UC-0C — Number That Looks Right

Per-ward, per-category budget growth calculator.
"""

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
    """Load and validate the budget CSV."""
    records = []

    with open(input_path, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        for row_number, row in enumerate(reader, start=2):
            actual_raw = (row.get("actual_spend") or "").strip()

            if actual_raw == "":
                actual_spend = None
            else:
                try:
                    actual_spend = float(actual_raw)
                except ValueError:
                    raise ValueError(
                        f"Invalid actual_spend at CSV row {row_number}: "
                        f"{actual_raw}"
                    )

            records.append(
                {
                    "period": row["period"].strip(),
                    "ward": row["ward"].strip(),
                    "category": row["category"].strip(),
                    "budgeted_amount": float(row["budgeted_amount"]),
                    "actual_spend": actual_spend,
                    "notes": (row.get("notes") or "").strip(),
                }
            )

    null_rows = [
        row for row in records if row["actual_spend"] is None
    ]

    print(f"Loaded {len(records)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for row in null_rows:
        print(
            f"NULL: {row['period']} | {row['ward']} | "
            f"{row['category']} | {row['notes']}"
        )

    return records


def compute_growth(records, ward, category, growth_type):
    """Compute growth for exactly one ward and one category."""

    if not growth_type:
        raise ValueError(
            "growth_type is required. Specify --growth-type, for example MoM."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "This implementation supports MoM only."
        )

    selected = [
        row
        for row in records
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []

    previous = None

    for row in selected:
        current = row["actual_spend"]

        if current is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": "",
                    "growth_type": "MoM",
                    "formula": "",
                    "growth_percent": "",
                    "flag": f"NULL actual_spend: {row['notes']}",
                }
            )
            previous = None
            continue

        if previous is None:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current,
                    "growth_type": "MoM",
                    "formula": "N/A — no previous non-null month",
                    "growth_percent": "",
                    "flag": "NO_PREVIOUS_VALUE",
                }
            )
            previous = current
            continue

        if previous == 0:
            results.append(
                {
                    "ward": ward,
                    "category": category,
                    "period": row["period"],
                    "actual_spend": current,
                    "growth_type": "MoM",
                    "formula": "N/A — previous actual_spend is zero",
                    "growth_percent": "",
                    "flag": "ZERO_PREVIOUS_VALUE",
                }
            )
            previous = current
            continue

        growth = ((current - previous) / previous) * 100

        formula = (
            f"(({current:.1f} - {previous:.1f}) / "
            f"{previous:.1f}) * 100"
        )

        results.append(
            {
                "ward": ward,
                "category": category,
                "period": row["period"],
                "actual_spend": current,
                "growth_type": "MoM",
                "formula": formula,
                "growth_percent": round(growth, 1),
                "flag": "",
            }
        )

        previous = current

    return results


def write_output(output_path, results):
    """Write per-period growth results to CSV."""

    fields = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "flag",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C municipal budget growth calculator"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    records = load_dataset(args.input)

    # Explicitly reject aggregate-style requests.
    if args.ward.lower() in {"all", "all wards", "*"}:
        raise ValueError(
            "Refusing all-ward aggregation. Specify exactly one ward."
        )

    if args.category.lower() in {"all", "all categories", "*"}:
        raise ValueError(
            "Refusing all-category aggregation. Specify exactly one category."
        )

    results = compute_growth(
        records,
        args.ward,
        args.category,
        args.growth_type,
    )

    write_output(args.output, results)

    print(f"Results written to: {args.output}")


if __name__ == "__main__":
    main()