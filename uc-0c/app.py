"""
UC-0C — Number That Looks Right
Deterministic municipal budget growth calculation engine.
Enforces per-ward/category granularity, explicit null reporting, and formula transparency.
"""
import argparse
import csv
import os
import sys

ALLOWED_GROWTH_TYPES = {"MoM", "YoY"}

def load_dataset(input_path: str):
    """Load CSV, validate columns, and identify null actual_spend values."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    records = []
    null_records = []

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing_cols = required_cols - set(reader.fieldnames or [])
        if missing_cols:
            raise ValueError(f"CSV is missing required columns: {missing_cols}")

        for idx, row in enumerate(reader, start=1):
            spend_raw = row["actual_spend"].strip()
            is_null = spend_raw == "" or spend_raw.lower() == "null"
            parsed_spend = None if is_null else float(spend_raw)

            clean_row = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": float(row["budgeted_amount"].strip()),
                "actual_spend": parsed_spend,
                "notes": row["notes"].strip(),
                "is_null": is_null,
                "row_num": idx
            }
            records.append(clean_row)
            if is_null:
                null_records.append(clean_row)

    print(f"Loaded {len(records)} rows from {input_path}.")
    print(f"Detected {len(null_records)} deliberate null actual_spend rows:")
    for nr in null_records:
        print(f"  - Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: '{nr['notes']}'")

    return records

def compute_growth(records, ward: str, category: str, growth_type: str):
    """Compute per-period growth without silent aggregation or silent null coercion."""
    if not ward or ward.lower() in ["all", "any", "total"]:
        raise ValueError("REFUSAL: All-ward aggregation is strictly prohibited. You must specify a single ward.")

    if not category or category.lower() in ["all", "any", "total"]:
        raise ValueError("REFUSAL: All-category aggregation is strictly prohibited. You must specify a single category.")

    if growth_type not in ALLOWED_GROWTH_TYPES:
        raise ValueError(f"REFUSAL: --growth-type must be specified as one of {ALLOWED_GROWTH_TYPES}. Never assume.")

    # Filter for exact ward and category
    filtered = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No records found for ward '{ward}' and category '{category}'.")

    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])

    output_rows = []
    formula_desc = "((Current - Previous) / Previous) * 100"

    for i, curr in enumerate(filtered):
        period = curr["period"]
        spend = curr["actual_spend"]
        budget = curr["budgeted_amount"]
        notes = curr["notes"]

        if curr["is_null"]:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": "NULL",
                "growth_type": growth_type,
                "growth_pct": "NULL",
                "formula": f"Cannot compute: actual_spend is NULL ({notes})",
                "flag": "FLAGGED_NULL",
                "notes": notes
            })
            continue

        if i == 0:
            # Baseline period: no prior period
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget,
                "actual_spend": f"{spend:.1f}",
                "growth_type": growth_type,
                "growth_pct": "N/A",
                "formula": "Baseline period (no prior period to compare)",
                "flag": "",
                "notes": notes
            })
        else:
            prev = filtered[i - 1]
            if prev["is_null"]:
                output_rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budget,
                    "actual_spend": f"{spend:.1f}",
                    "growth_type": growth_type,
                    "growth_pct": "N/A",
                    "formula": f"Cannot compute: previous period {prev['period']} was NULL",
                    "flag": "PREV_PERIOD_NULL",
                    "notes": notes
                })
            else:
                prev_spend = prev["actual_spend"]
                if prev_spend == 0:
                    growth_val = 0.0
                else:
                    growth_val = ((spend - prev_spend) / prev_spend) * 100.0

                sign = "+" if growth_val > 0 else ""
                growth_str = f"{sign}{growth_val:.1f}%"
                calc_formula = f"(({spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100 = {growth_str}"

                output_rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "budgeted_amount": budget,
                    "actual_spend": f"{spend:.1f}",
                    "growth_type": growth_type,
                    "growth_pct": growth_str,
                    "formula": calc_formula,
                    "flag": "",
                    "notes": notes
                })

    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Expenditure Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="Growth metric to calculate")
    parser.add_argument("--output", required=True, help="Path to write output growth CSV")
    args = parser.parse_args()

    records = load_dataset(args.input)
    results = compute_growth(records, args.ward, args.category, args.growth_type)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period", "ward", "category", "budgeted_amount",
        "actual_spend", "growth_type", "growth_pct", "formula", "flag", "notes"
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults successfully written to: {args.output}")
    print("\n--- Computed Trajectory ---")
    for r in results:
        flag_str = f" [{r['flag']}]" if r['flag'] else ""
        print(f"  {r['period']} | Spend: {r['actual_spend']:>6} | Growth: {r['growth_pct']:>8}{flag_str} | {r['formula']}")

if __name__ == "__main__":
    main()