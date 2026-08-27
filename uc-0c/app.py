"""
UC-0C app.py — Budget Growth Calculator (Number That Looks Right)
Built following RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple, Any


def load_dataset(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Reads CSV, validates columns, audits null values with reasons from notes,
    and returns (records, null_audit_list).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    records = []
    null_audit = []

    with open(file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing_cols = required_columns - fieldnames
        if missing_cols:
            raise ValueError(f"Missing required columns in dataset: {missing_cols}")

        for row_idx, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            budgeted_str = row.get("budgeted_amount", "").strip()
            actual_str = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()

            is_null = actual_str == "" or actual_str.lower() in ("null", "none", "nan")

            rec = {
                "row_num": row_idx,
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": float(budgeted_str) if budgeted_str else 0.0,
                "actual_spend": None if is_null else float(actual_str),
                "notes": notes,
            }
            records.append(rec)

            if is_null:
                null_audit.append(rec)

    return records, null_audit


def compute_growth(
    records: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, Any]]:
    """
    Computes per-period growth (MoM or YoY) for a single ward-category pair.
    Refuses whole-city or multi-ward blending.
    Displays formulas and handles nulls transparently.
    """
    if not growth_type:
        raise ValueError(
            "Refusal: --growth-type must be specified explicitly (MoM or YoY). Formula assumptions are strictly prohibited."
        )

    norm_growth_type = growth_type.strip().upper()
    if norm_growth_type not in ("MOM", "YOY"):
        raise ValueError(
            f"Refusal: Unsupported growth type '{growth_type}'. Allowed types are 'MoM' or 'YoY'."
        )

    # Prevent cross-ward or cross-category blending
    if not ward or ward.lower() in ("all", "citywide", "all wards", "total"):
        raise ValueError(
            "Refusal: Aggregation across multiple wards into a single blended number is prohibited. Specify an individual ward."
        )

    if not category or category.lower() in ("all", "all categories", "total"):
        raise ValueError(
            "Refusal: Aggregation across multiple categories into a single blended number is prohibited. Specify an individual category."
        )

    # Filter records
    matching = [r for r in records if r["ward"] == ward and r["category"] == category]
    if not matching:
        available_wards = sorted(list(set(r["ward"] for r in records)))
        available_cats = sorted(list(set(r["category"] for r in records)))
        raise ValueError(
            f"No records found for ward='{ward}' and category='{category}'.\n"
            f"Available wards: {available_wards}\n"
            f"Available categories: {available_cats}"
        )

    # Sort chronologically by period
    matching.sort(key=lambda r: r["period"])

    results = []
    prev_spend_val = None
    prev_period_was_null = False

    for idx, rec in enumerate(matching):
        period = rec["period"]
        budgeted = f"{rec['budgeted_amount']:.1f}"
        actual = rec["actual_spend"]
        notes = rec["notes"]

        if actual is None:
            # Current row is NULL
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "previous_spend": f"{prev_spend_val:.1f}" if prev_spend_val is not None else "n/a",
                "growth_percent": "n/a",
                "formula": f"Cannot compute: actual_spend is NULL ({notes})" if notes else "Cannot compute: actual_spend is NULL",
                "status": "NULL_ACTUAL_SPEND",
            })
            prev_spend_val = None
            prev_period_was_null = True
            continue

        actual_str = f"{actual:.1f}"

        if idx == 0:
            # Baseline period (first period in series)
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual_str,
                "previous_spend": "n/a",
                "growth_percent": "n/a",
                "formula": "Baseline period (no prior comparison period)",
                "status": "BASELINE",
            })
            prev_spend_val = actual
            prev_period_was_null = False
            continue

        if prev_period_was_null or prev_spend_val is None:
            # Previous period was NULL
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": actual_str,
                "previous_spend": "NULL",
                "growth_percent": "n/a",
                "formula": "Cannot compute: previous period actual_spend was NULL",
                "status": "PREVIOUS_PERIOD_NULL",
            })
            prev_spend_val = actual
            prev_period_was_null = False
            continue

        # Valid compute
        prev_spend_str = f"{prev_spend_val:.1f}"
        if prev_spend_val == 0:
            growth_val_str = "n/a"
            formula_str = f"({actual:.1f} - 0.0) / 0.0 * 100 (division by zero)"
            status_str = "DIV_ZERO"
        else:
            growth_pct = ((actual - prev_spend_val) / prev_spend_val) * 100.0
            growth_val_str = f"{growth_pct:+.1f}%"
            formula_str = f"({actual:.1f} - {prev_spend_val:.1f}) / {prev_spend_val:.1f} * 100"
            status_str = "OK"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_str,
            "previous_spend": prev_spend_str,
            "growth_percent": growth_val_str,
            "formula": formula_str,
            "status": status_str,
        })

        prev_spend_val = actual
        prev_period_was_null = False

    return results


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator (Number That Looks Right)"
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Target ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument(
        "--category", required=True, help="Target category (e.g. 'Roads & Pothole Repair')"
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        choices=["MoM", "YoY", "mom", "yoy"],
        help="Growth calculation type (MoM or YoY). Mandatory.",
    )
    parser.add_argument("--output", required=True, help="Path to write output growth CSV")
    args = parser.parse_args()

    # 1. Load dataset & audit nulls
    records, null_audit = load_dataset(args.input)
    print(f"Loaded dataset: {len(records)} rows from {args.input}")
    print(f"Null Audit: Found {len(null_audit)} deliberate null actual_spend rows:")
    for n in null_audit:
        print(f"  • Row {n['row_num']}: {n['period']} | {n['ward']} | {n['category']} | Reason: {n['notes']}")

    # 2. Compute per-ward per-category growth
    growth_results = compute_growth(records, args.ward, args.category, args.growth_type)

    # 3. Write output CSV
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "previous_spend",
        "growth_percent",
        "formula",
        "status",
    ]

    with open(args.output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_results)

    print(f"\nGrowth computation complete for '{args.ward}' - '{args.category}' ({args.growth_type.upper()}).")
    print(f"Results written to: {args.output}\n")

    # Display console table preview
    print(f"{'Period':<10} | {'Budget':<8} | {'Actual':<8} | {'Prev':<8} | {'Growth':<10} | {'Status':<18} | {'Formula'}")
    print("-" * 95)
    for r in growth_results:
        print(
            f"{r['period']:<10} | {r['budgeted_amount']:<8} | {r['actual_spend']:<8} | "
            f"{r['previous_spend']:<8} | {r['growth_percent']:<10} | {r['status']:<18} | {r['formula']}"
        )


if __name__ == "__main__":
    main()

