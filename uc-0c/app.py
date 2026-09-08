"""
UC-0C — Number That Looks Right
Budget Growth Analysis App enforcing the RICE framework:
- Disaggregated scope (strictly per-ward per-category, refusing aggregation)
- Transparent null handling (reporting null reasons from notes, never zeroing)
- Formula exposure (displaying exact formula used in each output row)
- Non-assumption of growth type (refusing execution if --growth-type not specified)
"""
import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


def normalize_text(s: str) -> str:
    """Normalize dashes and whitespace for robust string matching."""
    return s.replace("–", "-").replace("—", "-").strip().lower()


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Load CSV, validate columns, and audit for null actual_spend rows.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input budget file not found: {file_path}")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    records = []
    null_rows = []
    wards = set()
    categories = set()

    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for col in required_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"Schema violation: missing required column '{col}'")

        for idx, row in enumerate(reader, start=2):
            records.append(row)
            wards.add(row["ward"].strip())
            categories.add(row["category"].strip())

            spend = row.get("actual_spend", "").strip()
            if spend == "":
                null_rows.append(
                    {
                        "row_num": idx,
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row["notes"],
                    }
                )

    print(f"[AUDIT] Loaded {len(records)} records from {file_path}.")
    print(f"[AUDIT] Detected {len(null_rows)} deliberately null actual_spend rows:")
    for nr in null_rows:
        print(f"  - Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")

    return {
        "records": records,
        "null_rows": null_rows,
        "wards": sorted(list(wards)),
        "categories": sorted(list(categories)),
    }


def compute_growth(
    dataset: Dict[str, Any],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str,
) -> List[Dict[str, Any]]:
    """
    Compute per-period growth rate for specified ward and category.
    Writes output table to CSV with formulas and null indicators.
    """
    norm_ward = normalize_text(ward)
    norm_cat = normalize_text(category)

    # Filter matching rows
    matching_rows = []
    for r in dataset["records"]:
        if normalize_text(r["ward"]) == norm_ward and normalize_text(r["category"]) == norm_cat:
            matching_rows.append(r)

    if not matching_rows:
        raise ValueError(
            f"No matching records found for ward='{ward}' and category='{category}'. "
            f"Available wards: {dataset['wards']}, Available categories: {dataset['categories']}"
        )

    matching_rows.sort(key=lambda r: r["period"])
    results = []
    prev_spend: Optional[float] = None

    for i, r in enumerate(matching_rows):
        period = r["period"]
        ward_name = r["ward"]
        category_name = r["category"]
        budgeted = r["budgeted_amount"]
        spend_raw = r["actual_spend"].strip()
        note = r.get("notes", "").strip()

        if spend_raw == "":
            actual_spend_display = "NULL"
            growth_pct = "NULL [FLAGGED]"
            formula = f"n/a (Actual spend is NULL: {note})"
            prev_spend = None  # break chain of comparison
        else:
            current_spend = float(spend_raw)
            actual_spend_display = f"{current_spend:.1f}"

            if prev_spend is None:
                growth_pct = "n/a (baseline)"
                if i == 0:
                    formula = "Baseline period (first month of observation)"
                else:
                    formula = "Baseline period (prior period spend was NULL or missing)"
            else:
                growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                growth_pct = f"{growth_val:+.1f}%"
                formula = f"(({current_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"

            prev_spend = current_spend

        results.append(
            {
                "period": period,
                "ward": ward_name,
                "category": category_name,
                "budgeted_amount": budgeted,
                "actual_spend": actual_spend_display,
                "growth_type": growth_type,
                "growth_pct": growth_pct,
                "formula": formula,
                "notes": note,
            }
        )

    # Write output to CSV
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_pct",
        "formula",
        "notes",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C — Municipal Budget Growth Analysis")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Specific ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, default=None, help="Specific category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, default=None, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=False, default="growth_output.csv", help="Output CSV path")
    args = parser.parse_args()

    # Enforcement Rule 4: Refuse if growth-type is not specified
    if not args.growth_type:
        print(
            "REFUSAL: Growth type not specified. "
            "Municipal audit standards prohibit silent formula assumptions. "
            "Please explicitly provide --growth-type MoM or --growth-type YoY.",
            file=sys.stderr,
        )
        sys.exit(1)

    growth_type = args.growth_type.strip()
    if growth_type.upper() not in ["MOM", "YOY"]:
        print(
            f"REFUSAL: Invalid growth type '{args.growth_type}'. "
            "Allowed values are strictly 'MoM' or 'YoY'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Enforcement Rule 1: Refuse all-ward or cross-category aggregation
    if not args.ward or args.ward.strip().lower() in ["all", "any", "total", "combined"]:
        print(
            "REFUSAL: All-ward aggregation is strictly prohibited. "
            "Expenditure growth must be analyzed per-ward. "
            "Please specify a specific --ward (e.g. --ward 'Ward 1 – Kasba').",
            file=sys.stderr,
        )
        sys.exit(1)

    if not args.category or args.category.strip().lower() in ["all", "any", "total", "combined"]:
        print(
            "REFUSAL: Cross-category aggregation is strictly prohibited. "
            "Expenditure growth must be analyzed per-category. "
            "Please specify a specific --category (e.g. --category 'Roads & Pothole Repair').",
            file=sys.stderr,
        )
        sys.exit(1)

    dataset = load_dataset(args.input)
    results = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=growth_type.upper(),
        output_path=args.output,
    )

    print(f"\n[SUCCESS] Growth calculations successfully written to {args.output}")
    print(f"[SUMMARY] Ward: {args.ward} | Category: {args.category} | Type: {growth_type.upper()}")
    print("-" * 80)
    for r in results:
        print(f"{r['period']} | Spend: {r['actual_spend']:>5} | Growth: {r['growth_pct']:>15} | Formula: {r['formula']}")


if __name__ == "__main__":
    main()
