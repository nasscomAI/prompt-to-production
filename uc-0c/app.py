"""
UC-0C — Budget Growth Calculator

Implements:
- RICE-style workflow
- Dataset validation
- Explicit ward/category selection
- Explicit growth-type requirement
- Null detection and reporting
- Per-period growth calculation
- Formula shown for every calculated row
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


def load_dataset(input_file):
    """
    Skill: load_dataset

    Reads and validates the CSV and reports every null actual_spend row.
    """

    path = Path(input_file)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {input_file}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {input_file}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    if not rows:
        raise ValueError("CSV dataset is empty.")

    null_rows = []

    for row in rows:
        actual = row["actual_spend"].strip()

        if actual == "":
            null_rows.append(row)

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend rows: {len(null_rows)}")

    if null_rows:
        print("\nNULL ROWS — NOT USED FOR GROWTH CALCULATION:")

        for row in null_rows:
            print(
                f"- {row['period']} | "
                f"{row['ward']} | "
                f"{row['category']} | "
                f"Reason: {row['notes']}"
            )

    return rows


def build_rice_prompt(rows, ward, category, growth_type):
    """
    Builds the RICE prompt required by the workflow.
    """

    return f"""
ROLE:
You are a budget growth analysis agent.

INSTRUCTIONS:
- Calculate growth only for the requested ward and category.
- Never aggregate across wards or categories.
- Use only the explicitly requested growth type.
- Never guess a growth type.
- Flag every null actual_spend before calculation.
- Use the reason from the notes column for null rows.
- Never calculate growth when the current or previous required value is null.
- Show the formula used for every calculated result.

CONTEXT:
Ward: {ward}
Category: {category}
Growth type: {growth_type}
Rows available: {len(rows)}

EXPECTED OUTPUT:
Return a per-period table containing the actual spend, formula, growth
result, and null status where applicable.
"""


def calculate_mom(rows):
    """
    Calculates Month-over-Month growth.

    Formula:
        ((current_month - previous_month) / previous_month) * 100
    """

    results = []

    previous_spend = None
    previous_period = None

    for row in rows:
        actual_text = row["actual_spend"].strip()

        if actual_text == "":
            results.append({
                "period": row["period"],
                "actual_spend": "",
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — current actual_spend is NULL",
                "growth": "",
                "status": f"NULL — {row['notes']}",
            })

            # A null month cannot be used as the previous value
            # for the following month's growth.
            previous_spend = None
            previous_period = row["period"]

            continue

        current_spend = float(actual_text)

        if previous_spend is None:
            results.append({
                "period": row["period"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": "NOT COMPUTED — no valid previous month actual_spend",
                "growth": "",
                "status": "Not computed",
            })
        else:
            growth = ((current_spend - previous_spend) / previous_spend) * 100

            formula = (
                f"(({current_spend:.2f} - {previous_spend:.2f}) "
                f"/ {previous_spend:.2f}) × 100"
            )

            results.append({
                "period": row["period"],
                "actual_spend": current_spend,
                "growth_type": "MoM",
                "formula": formula,
                "growth": round(growth, 1),
                "status": "Calculated",
            })

        previous_spend = current_spend
        previous_period = row["period"]

    return results


def calculate_yoy(rows):
    """
    Calculates Year-over-Year growth.

    The dataset contains only 2024 monthly data, so there is no previous-year
    value available. Therefore YoY cannot be calculated from this dataset.
    """

    results = []

    for row in rows:
        if row["actual_spend"].strip() == "":
            results.append({
                "period": row["period"],
                "actual_spend": "",
                "growth_type": "YoY",
                "formula": "NOT COMPUTED — current actual_spend is NULL",
                "growth": "",
                "status": f"NULL — {row['notes']}",
            })
        else:
            results.append({
                "period": row["period"],
                "actual_spend": float(row["actual_spend"]),
                "growth_type": "YoY",
                "formula": "NOT COMPUTED — previous-year data is unavailable",
                "growth": "",
                "status": "Not computed — no 2023 data",
            })

    return results


def compute_growth(rows, ward, category, growth_type):
    """
    Skill: compute_growth

    Filters to exactly one ward and category and calculates the requested
    growth type.
    """

    if not ward:
        raise ValueError(
            "Ward is required. All-ward aggregation is not permitted."
        )

    if not category:
        raise ValueError(
            "Category is required. Cross-category aggregation is not permitted."
        )

    if not growth_type:
        raise ValueError(
            "Growth type is required. Specify --growth-type; do not guess."
        )

    growth_type = growth_type.strip().upper()

    if growth_type not in {"MOM", "YOY"}:
        raise ValueError(
            f"Unsupported growth type: {growth_type}. "
            "Supported values are MoM and YoY."
        )

    filtered = [
        row
        for row in rows
        if row["ward"].strip() == ward.strip()
        and row["category"].strip() == category.strip()
    ]

    if not filtered:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    filtered.sort(key=lambda row: row["period"])

    if growth_type == "MOM":
        return calculate_mom(filtered)

    return calculate_yoy(filtered)


def write_output(output_file, ward, category, growth_type, results):
    """
    Writes the required per-period output CSV.
    """

    output_path = Path(output_file)

    fieldnames = [
        "ward",
        "category",
        "period",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
    ]

    with output_path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                "ward": ward,
                "category": category,
                "period": result["period"],
                "actual_spend": result["actual_spend"],
                "growth_type": result["growth_type"],
                "formula": result["formula"],
                "growth_percent": result["growth"],
                "status": result["status"],
            })


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type, e.g. MoM or YoY"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path"
    )

    args = parser.parse_args()

    # Load and validate dataset.
    rows = load_dataset(args.input)

    # Build RICE prompt for the workflow.
    rice_prompt = build_rice_prompt(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    # Keep prompt available for AI-tool integration.
    _ = rice_prompt

    # Compute requested growth.
    results = compute_growth(
        rows,
        args.ward,
        args.category,
        args.growth_type
    )

    # Write per-ward, per-category output.
    write_output(
        args.output,
        args.ward,
        args.category,
        args.growth_type,
        results
    )

    print(f"\nGrowth output written successfully to: {args.output}")


if __name__ == "__main__":
    main()