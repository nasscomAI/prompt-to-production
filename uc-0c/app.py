"""
UC-0C app.py — Budget Growth Calculator.
Built using RICE framework, agents.md, and skills.md.

Guarantees:
- Granular per-ward per-category computations (refuses multi-ward aggregation)
- Transparent null handling (identifies and flags missing actual spend with audit notes)
- Explicit mathematical formula reported in every output row
- Strict refusal on missing/ambiguous growth-type (never guesses MoM vs YoY)
"""
import argparse
import csv
import os
import sys


def load_dataset(file_path: str) -> dict:
    """
    Skill: load_dataset
    Reads the CSV, validates headers, and audits all null rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget dataset not found at: {file_path}")

    required_fields = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

    rows = []
    null_rows = []
    wards = set()
    categories = set()

    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not set(required_fields).issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV missing required columns: {required_fields}")

        for line_num, r in enumerate(reader, start=2):
            period = (r.get("period") or "").strip()
            ward = (r.get("ward") or "").strip()
            category = (r.get("category") or "").strip()
            notes = (r.get("notes") or "").strip()

            budgeted_raw = (r.get("budgeted_amount") or "").strip()
            actual_raw = (r.get("actual_spend") or "").strip()

            budgeted = float(budgeted_raw) if budgeted_raw else 0.0
            actual = float(actual_raw) if actual_raw else None

            row_data = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "actual_spend_raw": actual_raw,
                "notes": notes,
                "line_number": line_num,
            }
            rows.append(row_data)
            if ward:
                wards.add(ward)
            if category:
                categories.add(category)

            if actual is None:
                null_rows.append(row_data)

    return {
        "total_rows": len(rows),
        "rows": rows,
        "wards": sorted(list(wards)),
        "categories": sorted(list(categories)),
        "null_rows": null_rows,
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Computes period-over-period growth for a specific ward and category,
    enforcing formula transparency and transparent null status.
    """
    # Enforcement Rule 1: Refuse all-ward or all-category aggregations
    if not ward or ward.lower() in ("all", "any", "*", "combined", "city-wide", "citywide"):
        raise ValueError("Refusal: Aggregation across all wards is prohibited. Please specify a single ward.")
    if not category or category.lower() in ("all", "any", "*", "combined"):
        raise ValueError("Refusal: Aggregation across all categories is prohibited. Please specify a single category.")

    # Enforcement Rule 4: Refuse if growth_type is missing or ambiguous
    if not growth_type or growth_type.upper() not in ("MOM", "YOY"):
        raise ValueError("Refusal: --growth-type must be explicitly specified as MoM or YoY (formula guessing is prohibited).")

    growth_type = growth_type.upper()

    # Validate ward and category existence
    if ward not in dataset["wards"]:
        raise ValueError(f"Unknown ward '{ward}'. Allowed wards: {dataset['wards']}")
    if category not in dataset["categories"]:
        raise ValueError(f"Unknown category '{category}'. Allowed categories: {dataset['categories']}")

    # Filter and sort
    filtered = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda x: x["period"])

    results = []
    formula_template = (
        "(actual_spend[t] - actual_spend[t-1]) / actual_spend[t-1] * 100"
        if growth_type == "MOM"
        else "(actual_spend[t] - actual_spend[t-12]) / actual_spend[t-12] * 100"
    )

    offset = 1 if growth_type == "MOM" else 12

    for i, row in enumerate(filtered):
        period = row["period"]
        budgeted = row["budgeted_amount"]
        actual = row["actual_spend"]
        notes = row["notes"]

        if i < offset:
            # Baseline period without predecessor
            if actual is None:
                growth_rate = "NULL"
                status = "FLAGGED_NULL"
                formula_str = "N/A (Missing actual spend)"
            else:
                growth_rate = "N/A (Baseline)"
                status = "BASELINE"
                formula_str = f"Baseline period ({growth_type} comparison has no prior period)"
        else:
            prev_row = filtered[i - offset]
            prev_actual = prev_row["actual_spend"]

            if actual is None:
                growth_rate = "NULL"
                status = "FLAGGED_NULL"
                formula_str = formula_template
            elif prev_actual is None:
                growth_rate = "NULL"
                status = "FLAGGED_NULL_PREDECESSOR"
                formula_str = formula_template
                notes = f"Prior period ({prev_row['period']}) missing: {prev_row['notes']}"
            elif prev_actual == 0:
                growth_rate = "UNDEFINED"
                status = "DIVISION_BY_ZERO"
                formula_str = f"({actual:.1f} - 0.0) / 0.0 * 100"
            else:
                rate = ((actual - prev_actual) / prev_actual) * 100.0
                sign = "+" if rate > 0 else ""
                growth_rate = f"{sign}{rate:.1f}%"
                status = "COMPUTED"
                formula_str = f"({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f} * 100"

        actual_str = f"{actual:.1f}" if actual is not None else "NULL"
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{budgeted:.1f}",
            "actual_spend": actual_str,
            "growth_type": growth_type,
            "growth_rate": growth_rate,
            "formula": formula_str,
            "status": status,
            "notes": notes,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument(
        "--input",
        required=False,
        default="data/budget/ward_budget.csv",
        help="Path to ward_budget.csv",
    )
    parser.add_argument(
        "--ward",
        required=False,
        default="Ward 1 – Kasba",
        help="Ward name (e.g. 'Ward 1 – Kasba')",
    )
    parser.add_argument(
        "--category",
        required=False,
        default="Roads & Pothole Repair",
        help="Category name (e.g. 'Roads & Pothole Repair')",
    )
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        default="MoM",
        help="Growth type: 'MoM' or 'YoY' (must be explicitly provided)",
    )
    parser.add_argument(
        "--output",
        required=False,
        default="growth_output.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    # Handle relative path from uc-0c directory
    if not os.path.exists(input_path):
        alt_input = os.path.join("..", input_path)
        if os.path.exists(alt_input):
            input_path = alt_input

    # Step 1: Load and audit dataset
    dataset = load_dataset(input_path)
    print(f"Loaded {dataset['total_rows']} records. Audited {len(dataset['null_rows'])} deliberate null actual_spend rows:")
    for nr in dataset["null_rows"]:
        print(f"  • Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {nr['notes']}")

    # Step 2: Compute growth
    try:
        results = compute_growth(
            dataset=dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as e:
        print(f"\n[EXECUTION HALTED / REFUSAL] {e}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Write results to output CSV
    fieldnames = [
        "period", "ward", "category", "budgeted_amount", "actual_spend",
        "growth_type", "growth_rate", "formula", "status", "notes"
    ]

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nComputed {len(results)} period rows for '{args.ward}' / '{args.category}' ({args.growth_type}).")
    print(f"Results successfully written to: {output_path}")

    # Display preview table
    print("\n" + "=" * 80)
    print(f"{'Period':<10} | {'Budget':<8} | {'Actual':<8} | {'Growth':<12} | {'Status':<15} | {'Formula'}")
    print("-" * 80)
    for r in results:
        print(f"{r['period']:<10} | {r['budgeted_amount']:<8} | {r['actual_spend']:<8} | {r['growth_rate']:<12} | {r['status']:<15} | {r['formula']}")
    print("=" * 80)


if __name__ == "__main__":
    main()
