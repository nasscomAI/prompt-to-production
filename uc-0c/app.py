"""
UC-0C — Number That Looks Right

Computes ward/category infrastructure spend growth while enforcing:
- No silent cross-ward or cross-category aggregation
- Explicit null reporting
- Explicit growth formula
- Explicit growth type
"""

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


def load_dataset(input_file):
    """Load and validate the CSV, reporting every null actual_spend row."""

    try:
        with open(input_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )

            rows = list(reader)

    except (OSError, csv.Error) as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc

    null_rows = []

    for row in rows:
        value = (row.get("actual_spend") or "").strip()

        if value == "":
            null_rows.append(row)

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend rows: {len(null_rows)}")

    if null_rows:
        print("\nNULL ROWS — flagged before computation:")
        for row in null_rows:
            print(
                f"  {row['period']} | {row['ward']} | "
                f"{row['category']} | Reason: {row['notes']}"
            )

    return rows


def compute_growth(rows, ward, category, growth_type):
    """Compute growth for one ward/category using the requested growth type."""

    if not growth_type:
        raise ValueError(
            "Growth type must be specified. Refusing to guess."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "This UC currently requires MoM."
        )

    # Explicitly refuse aggregation requests.
    if ward.strip().lower() in {"all", "*", "all wards"}:
        raise ValueError(
            "Refusing all-ward aggregation. A specific ward is required."
        )

    if category.strip().lower() in {"all", "*", "all categories"}:
        raise ValueError(
            "Refusing cross-category aggregation. A specific category is required."
        )

    selected = [
        row
        for row in rows
        if row["ward"].strip() == ward.strip()
        and row["category"].strip() == category.strip()
    ]

    if not selected:
        raise ValueError(
            f"No rows found for ward='{ward}' and category='{category}'."
        )

    selected.sort(key=lambda row: row["period"])

    results = []

    previous_spend = None
    previous_period = None

    for row in selected:
        current_raw = (row.get("actual_spend") or "").strip()

        if current_raw == "":
            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": (
                        "" if previous_spend is None else f"{previous_spend:.2f}"
                    ),
                    "actual_spend": "",
                    "formula": "NOT COMPUTED — actual_spend is NULL",
                    "growth": "",
                    "status": "FLAGGED: NULL",
                    "notes": row["notes"],
                }
            )

            # A null current value cannot become the previous value
            # for the next calculation.
            previous_spend = None
            previous_period = row["period"]
            continue

        current_spend = float(current_raw)

        if previous_spend is None:
            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": "",
                    "actual_spend": f"{current_spend:.2f}",
                    "formula": "NOT COMPUTED — no valid previous actual_spend",
                    "growth": "",
                    "status": "NOT COMPUTED",
                    "notes": "",
                }
            )
        else:
            growth = (
                (current_spend - previous_spend)
                / previous_spend
                * 100
            )

            formula = (
                f"(({current_spend:.2f} - {previous_spend:.2f}) "
                f"/ {previous_spend:.2f}) × 100 = {growth:+.1f}%"
            )

            results.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "previous_actual_spend": f"{previous_spend:.2f}",
                    "actual_spend": f"{current_spend:.2f}",
                    "formula": formula,
                    "growth": f"{growth:+.1f}%",
                    "status": "COMPUTED",
                    "notes": "",
                }
            )

        previous_spend = current_spend
        previous_period = row["period"]

    return results


def write_output(output_file, results):
    """Write the per-period results to CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "previous_actual_spend",
        "actual_spend",
        "formula",
        "growth",
        "status",
        "notes",
    ]

    try:
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except OSError as exc:
        raise ValueError(f"Could not write output: {exc}") from exc


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C ward-level infrastructure spend growth calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward budget CSV",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Specific ward to analyze",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Specific category to analyze",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth formula to use, e.g. MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path",
    )

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

        print(f"\nOutput written to: {args.output}")
        print(f"Output rows: {len(results)}")

    except ValueError as exc:
        print(f"\nREFUSED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
