"""
UC-0C — Number That Looks Right

Deterministic ward/category growth calculator.
Uses only the supplied CSV and Python standard library.
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
    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing:
            raise ValueError(
                "Missing required columns: " + ", ".join(sorted(missing))
            )

        rows = list(reader)

    if not rows:
        raise ValueError("Dataset is empty.")

    null_rows = []

    for row in rows:
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": row["notes"],
                }
            )

    print(f"Loaded {len(rows)} rows.")
    print(f"Null actual_spend rows: {len(null_rows)}")

    for item in null_rows:
        print(
            f"NULL: {item['period']} | "
            f"{item['ward']} | "
            f"{item['category']} | "
            f"{item['reason']}"
        )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """Compute per-period growth for one ward and category."""

    if not growth_type:
        raise ValueError(
            "--growth-type is required. Do not guess the growth formula."
        )

    growth_type = growth_type.upper()

    if growth_type != "MOM":
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "Only MoM is supported."
        )

    selected = [
        row
        for row in rows
        if row["ward"] == ward and row["category"] == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []

    previous_actual = None
    previous_period = None

    for row in selected:
        period = row["period"]
        actual_text = row["actual_spend"].strip()
        notes = row["notes"]

        if actual_text == "":
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "formula": "Not computed — current actual_spend is NULL",
                    "growth_percent": "",
                    "status": f"FLAGGED NULL: {notes}",
                }
            )

            previous_actual = None
            previous_period = period
            continue

        actual = float(actual_text)

        if previous_actual is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual,
                    "formula": "Not computed — no valid previous month actual_spend",
                    "growth_percent": "",
                    "status": "BASE PERIOD",
                }
            )
        else:
            if previous_actual == 0:
                results.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual,
                        "formula": (
                            f"((current {actual:.1f} - previous "
                            f"{previous_actual:.1f}) / previous "
                            f"{previous_actual:.1f}) × 100 = undefined"
                        ),
                        "growth_percent": "",
                        "status": "NOT COMPUTED: previous value is zero",
                    }
                )
            else:
                growth = (
                    (actual - previous_actual)
                    / previous_actual
                ) * 100

                results.append(
                    {
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": actual,
                        "formula": (
                            f"(({actual:.1f} - {previous_actual:.1f}) "
                            f"/ {previous_actual:.1f}) × 100"
                        ),
                        "growth_percent": round(growth, 1),
                        "status": "OK",
                    }
                )

        previous_actual = actual
        previous_period = period

    return results


def write_output(results, output_path):
    """Write results to CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "formula",
        "growth_percent",
        "status",
    ]

    path = Path(output_path)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Output written to: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate per-period ward/category growth."
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

    write_output(results, args.output)


if __name__ == "__main__":
    main()