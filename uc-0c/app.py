"""
UC-0C — Number That Looks Right
Deterministic, granular municipal budget growth calculator adhering to RICE specification.
Enforces per-ward per-category computation, formula transparency, and proactive null data flagging.
"""
import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
ALLOWED_GROWTH_TYPES = ["MoM", "YoY"]


def load_dataset(input_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Load CSV, validate schema, audit and register all null actual_spend rows.
    Returns: (parsed_rows, null_rows_audit)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input budget file not found at: {input_path}")

    rows: List[Dict[str, Any]] = []
    null_rows: List[Dict[str, Any]] = []

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if not reader.fieldnames:
            raise ValueError(f"Empty or headerless CSV file: {input_path}")
            
        for col in REQUIRED_COLUMNS:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column in CSV schema: '{col}' (found: {reader.fieldnames})")

        for idx, r in enumerate(reader, start=2):
            period = str(r.get("period", "") or "").strip()
            ward = str(r.get("ward", "") or "").strip()
            category = str(r.get("category", "") or "").strip()
            notes = str(r.get("notes", "") or "").strip()

            budget_raw = str(r.get("budgeted_amount", "") or "").strip()
            budget_val = float(budget_raw) if budget_raw else 0.0

            actual_raw = str(r.get("actual_spend", "") or "").strip()
            actual_val: Optional[float] = None
            if actual_raw != "":
                try:
                    actual_val = float(actual_raw)
                except ValueError:
                    actual_val = None

            record = {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budget_val,
                "actual_spend": actual_val,
                "notes": notes,
                "row_num": idx,
            }

            rows.append(record)

            if actual_val is None:
                null_rows.append(record)

    return rows, null_rows


def compute_growth(
    dataset: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, Any]]:
    """
    Compute granular growth table per period.
    Strictly refuses all-ward/all-category aggregations and unparameterized growth types.
    """
    # Enforcement 1: Refuse growth-type guessing
    if not growth_type or growth_type.strip() not in ALLOWED_GROWTH_TYPES:
        raise ValueError(
            f"REFUSAL: --growth-type must be explicitly specified as one of {ALLOWED_GROWTH_TYPES} "
            f"(received: '{growth_type}'). Guessing or silent default selection is strictly prohibited."
        )

    # Enforcement 2: Refuse all-ward or all-category aggregations
    ward_clean = ward.strip() if ward else ""
    category_clean = category.strip() if category else ""

    forbidden_wildcards = ["all", "all wards", "all categories", "*", "total", "aggregate", "any"]

    if not ward_clean or ward_clean.lower() in forbidden_wildcards:
        raise ValueError(
            "REFUSAL: Aggregation across all wards is strictly prohibited by RICE enforcement rules. "
            "Calculations must be requested for a specific named ward."
        )

    if not category_clean or category_clean.lower() in forbidden_wildcards:
        raise ValueError(
            "REFUSAL: Aggregation across all categories is strictly prohibited by RICE enforcement rules. "
            "Calculations must be requested for a specific named category."
        )

    # Filter dataset
    filtered = [
        r for r in dataset
        if r["ward"].strip().lower() == ward_clean.lower()
        and r["category"].strip().lower() == category_clean.lower()
    ]

    if not filtered:
        raise ValueError(
            f"No data rows found matching Ward: '{ward_clean}' and Category: '{category_clean}'."
        )

    # Sort sequentially by period
    filtered.sort(key=lambda x: x["period"])

    results: List[Dict[str, Any]] = []

    if growth_type == "MoM":
        for i, curr_row in enumerate(filtered):
            period = curr_row["period"]
            budget = curr_row["budgeted_amount"]
            actual = curr_row["actual_spend"]
            notes = curr_row["notes"]
            actual_display = f"{actual:.1f}" if actual is not None else ""

            if actual is None:
                # Enforcement 3: Flag null row
                reason = notes if notes else "Data missing / unsubmitted"
                results.append({
                    "period": period,
                    "ward": curr_row["ward"],
                    "category": curr_row["category"],
                    "budgeted_amount": f"{budget:.1f}",
                    "actual_spend": actual_display,
                    "growth_type": "MoM",
                    "growth_rate": "NULL (Data Missing)",
                    "formula": "actual_spend is NULL; calculation flagged and omitted",
                    "status": "FLAGGED_NULL",
                    "notes": reason,
                })
                continue

            if i == 0:
                results.append({
                    "period": period,
                    "ward": curr_row["ward"],
                    "category": curr_row["category"],
                    "budgeted_amount": f"{budget:.1f}",
                    "actual_spend": actual_display,
                    "growth_type": "MoM",
                    "growth_rate": "N/A (First Period)",
                    "formula": "Base period - no prior month available",
                    "status": "BASE_PERIOD",
                    "notes": notes,
                })
                continue

            prev_row = filtered[i - 1]
            prev_actual = prev_row["actual_spend"]

            if prev_actual is None:
                results.append({
                    "period": period,
                    "ward": curr_row["ward"],
                    "category": curr_row["category"],
                    "budgeted_amount": f"{budget:.1f}",
                    "actual_spend": actual_display,
                    "growth_type": "MoM",
                    "growth_rate": "N/A (Prior Period Null)",
                    "formula": f"Prior period ({prev_row['period']}) actual_spend was NULL; MoM undefined",
                    "status": "FLAGGED_PRIOR_NULL",
                    "notes": notes,
                })
                continue

            # Standard MoM calculation
            growth_pct = ((actual - prev_actual) / prev_actual) * 100.0
            growth_rate_str = f"{growth_pct:+.1f}%"
            formula_str = f"({actual:.1f} - {prev_actual:.1f}) / {prev_actual:.1f} * 100"

            results.append({
                "period": period,
                "ward": curr_row["ward"],
                "category": curr_row["category"],
                "budgeted_amount": f"{budget:.1f}",
                "actual_spend": actual_display,
                "growth_type": "MoM",
                "growth_rate": growth_rate_str,
                "formula": formula_str,
                "status": "COMPUTED",
                "notes": notes,
            })

    elif growth_type == "YoY":
        raise NotImplementedError("YoY growth requires multiple years of baseline data (2024 dataset covers 1 year).")

    return results


def write_growth_output(records: List[Dict[str, Any]], output_path: str):
    """Write computed growth table to CSV."""
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

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Specific category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth metric: 'MoM' or 'YoY'")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Load dataset and audit nulls
    try:
        dataset, null_rows = load_dataset(args.input)
        print(f"Loaded {len(dataset)} rows from {args.input}. Detected {len(null_rows)} deliberate null spend rows:")
        for nr in null_rows:
            print(f"  • Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} -> Null Reason: {nr['notes']}")
    except Exception as e:
        print(f"Data loading error: {e}", file=sys.stderr)
        sys.exit(1)

    # Compute growth
    try:
        results = compute_growth(
            dataset=dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
        write_growth_output(results, args.output)
        print(f"\nGrowth computation complete. Wrote {len(results)} rows to {args.output}")
        for r in results:
            print(f"  [{r['period']}] Spend: {r['actual_spend']:>5} | Growth: {r['growth_rate']:>18} | Formula: {r['formula']}")
    except ValueError as ve:
        print(f"\n{ve}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
