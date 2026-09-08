"""
UC-0C app.py — Budget Growth Calculator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Enforces granular per-ward per-category computation, null flagging, and refusal of all-ward aggregation.
"""
import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


def normalize_string(val: str) -> str:
    """Normalize dashes and spaces for robust matching."""
    if not val:
        return ""
    # Normalize unicode dashes (en-dash, em-dash, hyphen)
    s = re.sub(r"[\u2010-\u2015\u2212-]", "-", val)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def load_dataset(file_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Load CSV, validate structure, scan for null actual_spend rows,
    and print null report before returning dataset.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget file not found: {file_path}")

    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows: List[Dict[str, str]] = []
    null_rows: List[Dict[str, str]] = []

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing_cols = required_cols - set(reader.fieldnames or [])
        if missing_cols:
            raise ValueError(f"Missing required columns in dataset: {missing_cols}")

        for r in reader:
            rows.append(r)
            actual = r.get("actual_spend", "").strip()
            if actual == "" or actual.lower() in ["null", "none", "nan"]:
                null_rows.append(r)

    print(f"[load_dataset] Successfully loaded {len(rows)} rows from {file_path}.")
    print(f"[load_dataset] Identified {len(null_rows)} deliberate null actual_spend rows:")
    for nr in null_rows:
        print(f"  • {nr.get('period')} | {nr.get('ward')} | {nr.get('category')} | Note: {nr.get('notes')}")

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]],
    target_ward: str,
    target_category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Calculate per-period expenditure growth for a specified ward and category.
    Strictly refuses cross-ward / cross-category aggregation.
    """
    if not growth_type:
        raise ValueError("Refused: --growth-type is required. Options: MoM, YoY. System refuses to guess.")

    norm_growth_type = growth_type.strip().upper()
    if norm_growth_type not in ["MOM", "YOY"]:
        raise ValueError(f"Refused: Unsupported growth-type '{growth_type}'. Must be MoM or YoY.")

    # Refuse all-ward aggregation attempts
    norm_w = normalize_string(target_ward)
    norm_c = normalize_string(target_category)

    refusal_keywords = ["all", "combined", "total", "citywide", "entire", "any", "*"]
    if norm_w in refusal_keywords or not target_ward:
        raise ValueError(
            "Refused: Aggregating across multiple wards obscures ward-level variances. "
            "Please specify an individual ward (e.g. 'Ward 1 – Kasba')."
        )
    if norm_c in refusal_keywords or not target_category:
        raise ValueError(
            "Refused: Aggregating across multiple categories obscures category variances. "
            "Please specify an individual category (e.g. 'Roads & Pothole Repair')."
        )

    # Filter matching rows
    matched_rows = []
    for r in rows:
        if normalize_string(r["ward"]) == norm_w and normalize_string(r["category"]) == norm_c:
            matched_rows.append(r)

    if not matched_rows:
        available_wards = sorted(list({r["ward"] for r in rows}))
        available_cats = sorted(list({r["category"] for r in rows}))
        raise ValueError(
            f"No data matching ward='{target_ward}' and category='{target_category}'.\n"
            f"Available wards: {available_wards}\nAvailable categories: {available_cats}"
        )

    # Sort by period
    matched_rows.sort(key=lambda x: x["period"])

    results = []
    prev_spend: Optional[float] = None

    for i, r in enumerate(matched_rows):
        period = r["period"]
        ward = r["ward"]
        cat = r["category"]
        budget = r["budgeted_amount"]
        raw_actual = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        is_null = raw_actual == "" or raw_actual.lower() in ["null", "none", "nan"]

        if is_null:
            growth_rate = "NULL"
            formula = "N/A (actual_spend is NULL)"
            status = "NULL_RECORD"
            current_spend = None
        else:
            current_spend = float(raw_actual)
            if i == 0:
                growth_rate = "N/A"
                formula = "Baseline period (no prior month)"
                status = "BASELINE"
            elif prev_spend is None:
                growth_rate = "N/A"
                formula = "N/A (prior period spend was NULL)"
                status = "PRIOR_NULL"
            else:
                pct = ((current_spend - prev_spend) / prev_spend) * 100.0
                sign = "+" if pct > 0 else ""
                growth_rate = f"{sign}{pct:.1f}%"
                formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100 = {growth_rate}"
                status = "COMPUTED"

        results.append({
            "period": period,
            "ward": ward,
            "category": cat,
            "budgeted_amount": budget,
            "actual_spend": raw_actual if not is_null else "NULL",
            "growth_type": norm_growth_type,
            "growth_rate": growth_rate,
            "formula": formula,
            "status": status,
            "notes": notes,
        })

        prev_spend = current_spend

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=False, default="growth_output.csv", help="Path to write output CSV")
    args = parser.parse_args()

    # If parameters missing, refuse and prompt rather than guessing
    if not args.ward or not args.category or not args.growth_type:
        print(
            "ERROR: Refused to calculate. Missing required parameters.\n"
            "Both --ward, --category, and --growth-type must be explicitly specified.\n"
            "System does not aggregate across wards or assume default formulas.\n"
            "Example:\n"
            '  python app.py --input ../data/budget/ward_budget.csv --ward "Ward 1 – Kasba" '
            '--category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv'
        )
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)

    try:
        growth_table = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate",
        "formula",
        "status",
        "notes",
    ]
    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_table)

    print(f"\n[compute_growth] Successfully generated {len(growth_table)} rows for {args.ward} | {args.category}:")
    for r in growth_table:
        print(f"  {r['period']}: Spend={r['actual_spend']} | Growth={r['growth_rate']} | Formula={r['formula']}")

    print(f"\nDone. Output written to {args.output}")


if __name__ == "__main__":
    main()

