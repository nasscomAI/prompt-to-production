"""
UC-0C app.py — Budget Growth Calculator
RICE-enforced municipal financial analysis script preventing wrong aggregation levels,
silent null dropping, and formula selection assumptions.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Optional


def load_dataset(input_path: str) -> List[Dict]:
    """
    Reads CSV, validates required columns, and parses floats while preserving NULLs.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    rows = []
    with open(input_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            b_amt = float(row["budgeted_amount"]) if row.get("budgeted_amount") else 0.0
            act_raw = row.get("actual_spend", "").strip()
            a_amt = float(act_raw) if act_raw != "" else None
            rows.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": b_amt,
                "actual_spend": a_amt,
                "notes": row.get("notes", "").strip(),
            })
    return rows


def compute_growth(
    dataset: List[Dict], ward: str, category: str, growth_type: str
) -> List[Dict]:
    """
    Calculates per-period growth (MoM or YoY) for a specific ward and category.
    Flags missing NULL actual_spend rows and includes exact mathematical formula.
    """
    # Filter dataset for target ward and category
    filtered = [
        r for r in dataset if r["ward"] == ward and r["category"] == category
    ]
    filtered.sort(key=lambda x: x["period"])

    if not filtered:
        raise ValueError(f"No records found for Ward: '{ward}' and Category: '{category}'")

    results = []
    formula_str = (
        "MoM Growth % = ((Actual_t - Actual_{t-1}) / Actual_{t-1}) * 100"
        if growth_type.upper() == "MOM"
        else "YoY Growth % = ((Actual_t - Actual_{t-12}) / Actual_{t-12}) * 100"
    )

    offset = 1 if growth_type.upper() == "MOM" else 12

    for i, row in enumerate(filtered):
        curr_spend = row["actual_spend"]
        curr_period = row["period"]
        budgeted = row["budgeted_amount"]
        notes = row["notes"]

        act_spend_display = f"{curr_spend:.1f}" if curr_spend is not None else "NULL"
        growth_pct = "N/A"
        flag_notes = notes

        if curr_spend is None:
            growth_pct = "N/A (Data Missing)"
            if not flag_notes:
                flag_notes = "Data missing / NULL spend record"
        elif i < offset:
            growth_pct = "N/A (Base Period)"
        else:
            prev_row = filtered[i - offset]
            prev_spend = prev_row["actual_spend"]

            if prev_spend is None:
                growth_pct = "N/A (Prior Period Missing)"
                prev_note = prev_row["notes"] or "NULL spend"
                flag_notes = f"Prior period ({prev_row['period']}) data missing: {prev_note}"
            elif prev_spend == 0:
                growth_pct = "N/A (Zero Prior Spend)"
            else:
                pct_val = ((curr_spend - prev_spend) / prev_spend) * 100.0
                if pct_val > 0:
                    growth_pct = f"+{pct_val:.1f}%"
                else:
                    growth_pct = f"{pct_val:.1f}%"

        results.append({
            "period": curr_period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{budgeted:.1f}",
            "actual_spend": act_spend_display,
            "growth_type": growth_type.upper(),
            "growth_percentage": growth_pct,
            "formula": formula_str,
            "flag_notes": flag_notes,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Target ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", help="Target expenditure category")
    parser.add_argument("--growth-type", help="Growth metric: MoM or YoY")
    parser.add_argument("--output", default="growth_output.csv", help="Path to write output CSV")
    args = parser.parse_args()

    # RICE Enforcement Rule 1: Refuse All-Ward or Cross-Category Aggregation
    if not args.ward or args.ward.strip().upper() in ["ALL", "ALL WARDS", "*"]:
        print("REFUSAL: All-ward aggregation is strictly prohibited. You must specify an explicit --ward parameter.", file=sys.stderr)
        sys.exit(1)

    if not args.category or args.category.strip().upper() in ["ALL", "ALL CATEGORIES", "*"]:
        print("REFUSAL: Cross-category aggregation is strictly prohibited. You must specify an explicit --category parameter.", file=sys.stderr)
        sys.exit(1)

    # RICE Enforcement Rule 4: Refuse Unspecified Growth Formulas
    if not args.growth_type or args.growth_type.strip().upper() not in ["MOM", "YOY"]:
        print("REFUSAL: --growth-type parameter missing or invalid. Must explicitly specify 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)

    dataset = load_dataset(args.input)
    growth_results = compute_growth(
        dataset, args.ward.strip(), args.category.strip(), args.growth_type.strip()
    )

    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_percentage",
        "formula",
        "flag_notes",
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"Growth calculation completed successfully. Results written to: {args.output}")


if __name__ == "__main__":
    main()
