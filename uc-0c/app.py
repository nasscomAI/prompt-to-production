"""
UC-0C app.py — Municipal Budget Growth Computation Engine.
Build following RICE + agents.md + skills.md + CRAFT workflow.

Enforces:
- Strict ward and category disaggregation (refuses all-ward aggregation)
- Null reporting & accounting (never silently skip or impute nulls)
- Explicit mathematical formula display per row
- Refusal when growth-type or required filters are missing
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """
    Skill: load_dataset
    Reads CSV, validates schema, and reports all null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    rows = []
    null_rows = []

    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            spend_str = row.get("actual_spend", "").strip()
            if spend_str == "" or spend_str.lower() in ["null", "none", "nan"]:
                null_rows.append({
                    "row_num": idx,
                    "period": row.get("period"),
                    "ward": row.get("ward"),
                    "category": row.get("category"),
                    "notes": row.get("notes", "No notes provided")
                })
            rows.append(row)

    print(f"Loaded {len(rows)} total records.")
    print(f"Null Audit: Found {len(null_rows)} records with missing actual_spend:")
    for nr in null_rows:
        print(f"  • Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Skill: compute_growth
    Filters data by ward and category, sorts by period, and calculates period-over-period growth.
    """
    # Enforcement: Refuse all-ward or all-category aggregation
    if not ward or ward.strip().lower() in ["all", "any", "all wards", "total"]:
        raise ValueError("REFUSAL: Aggregating across all wards is strictly prohibited as it obscures ward-level disparities.")
    if not category or category.strip().lower() in ["all", "any", "all categories", "total"]:
        raise ValueError("REFUSAL: Aggregating across all categories is strictly prohibited. Specify an exact category.")
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type must be explicitly specified (e.g., 'MoM').")
    if growth_type.upper() != "MOM":
        raise NotImplementedError(f"Growth type '{growth_type}' is not supported. Supported type: MoM.")

    # Filter target series
    series = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    if not series:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort sequentially by period
    series.sort(key=lambda r: r.get("period", ""))

    output_rows = []
    prev_spend = None

    for r in series:
        period = r.get("period")
        spend_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if spend_str == "" or spend_str.lower() in ["null", "none", "nan"]:
            actual_spend = None
        else:
            actual_spend = float(spend_str)

        if prev_spend is None and actual_spend is not None and not output_rows:
            # Baseline period (first month)
            growth_pct = "BASE"
            formula = "Baseline period — no prior period comparison"
            status = "BASELINE"
        elif actual_spend is None:
            growth_pct = "NULL"
            formula = "Cannot compute: current actual_spend is NULL"
            status = "FLAGGED_NULL_CURRENT"
        elif prev_spend is None:
            growth_pct = "NULL"
            formula = "Cannot compute: previous actual_spend is NULL"
            status = "FLAGGED_NULL_PREVIOUS"
        else:
            growth_val = ((actual_spend - prev_spend) / prev_spend) * 100.0
            sign = "+" if growth_val > 0 else ""
            growth_pct = f"{sign}{growth_val:.1f}%"
            formula = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
            status = "COMPUTED"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual_spend:.1f}" if actual_spend is not None else "NULL",
            "previous_spend": f"{prev_spend:.1f}" if prev_spend is not None else "N/A",
            "growth_type": growth_type.upper(),
            "growth_pct": growth_pct,
            "formula": formula,
            "status": status,
            "notes": notes
        })

        prev_spend = actual_spend

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (disaggregated)")
    parser.add_argument("--category", required=True, help="Category name (disaggregated)")
    parser.add_argument("--growth-type", required=True, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Output path for growth CSV")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    growth_results = compute_growth(rows, args.ward, args.category, args.growth_type)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    fieldnames = [
        "period", "ward", "category", "actual_spend", "previous_spend",
        "growth_type", "growth_pct", "formula", "status", "notes"
    ]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"\nSUCCESS: Growth analysis generated at {args.output}")
    print("Verification:")
    for r in growth_results:
        if r["period"] in ["2024-07", "2024-10"]:
            print(f"  • {r['period']}: Spend={r['actual_spend']} Lakh, MoM Growth={r['growth_pct']} ({r['formula']})")


if __name__ == "__main__":
    main()

