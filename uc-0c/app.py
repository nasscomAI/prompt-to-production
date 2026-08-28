"""
UC-0C Growth Calculator — Number That Looks Right
Conforms strictly to README.md, agents.md, and skills.md.

Failure modes addressed:
1. Wrong aggregation level — Refuses requests to aggregate across multiple/all wards or categories.
2. Silent null handling — Detects and flags every null actual_spend row with reason before computing.
3. Formula assumption — Requires explicit --growth-type; never assumes MoM/YoY.
"""

import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]

SUPPORTED_GROWTH_TYPES = {
    "MOM": {
        "name": "Month-over-Month (MoM)",
        "formula": "((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100"
    }
}

PROHIBITED_AGGREGATION_KEYWORDS = {"all", "all wards", "all categories", "total", "*", "combined", "any"}


def normalize_str(val: Optional[str]) -> str:
    """Normalize string for safe comparison (handling dashes and spacing)."""
    if not val:
        return ""
    return val.replace("–", "-").replace("—", "-").strip().lower()


def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Skill: load_dataset
    Reads the ward budget CSV, validates required columns, and identifies
    all rows containing null actual_spend values before calculations are performed.

    Returns:
        Dict with:
          - 'rows': List of all row dicts
          - 'null_rows': List of rows with null actual_spend
          - 'null_count': Total count of null rows
          - 'total_rows': Total row count
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget dataset file not found at: {file_path}")

    rows: List[Dict[str, str]] = []
    null_rows: List[Dict[str, Any]] = []

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

            # Validate required columns
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in headers]
            if missing_cols:
                raise ValueError(
                    f"Dataset validation error: Missing required column(s): {', '.join(missing_cols)}. "
                    f"Required columns are: {', '.join(REQUIRED_COLUMNS)}"
                )

            for line_idx, row in enumerate(reader, start=2):  # Line 1 is header
                cleaned_row = {k: (v.strip() if v is not None else "") for k, v in row.items()}
                rows.append(cleaned_row)

                actual_val = cleaned_row.get("actual_spend", "")
                if actual_val == "":
                    null_info = {
                        "line_number": line_idx,
                        "period": cleaned_row.get("period", ""),
                        "ward": cleaned_row.get("ward", ""),
                        "category": cleaned_row.get("category", ""),
                        "budgeted_amount": cleaned_row.get("budgeted_amount", ""),
                        "notes": cleaned_row.get("notes", "") or "No reason provided in notes"
                    }
                    null_rows.append(null_info)

    except UnicodeDecodeError:
        # Fallback with latin-1 if utf-8 fails
        with open(file_path, mode="r", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            missing_cols = [col for col in REQUIRED_COLUMNS if col not in headers]
            if missing_cols:
                raise ValueError(f"Dataset validation error: Missing required column(s): {', '.join(missing_cols)}")
            for line_idx, row in enumerate(reader, start=2):
                cleaned_row = {k: (v.strip() if v is not None else "") for k, v in row.items()}
                rows.append(cleaned_row)
                if cleaned_row.get("actual_spend", "") == "":
                    null_rows.append({
                        "line_number": line_idx,
                        "period": cleaned_row.get("period", ""),
                        "ward": cleaned_row.get("ward", ""),
                        "category": cleaned_row.get("category", ""),
                        "budgeted_amount": cleaned_row.get("budgeted_amount", ""),
                        "notes": cleaned_row.get("notes", "") or "No reason provided in notes"
                    })

    # Report null detection before any calculations
    print("=" * 80)
    print(f"DATASET VALIDATION REPORT: {file_path}")
    print(f"Total Rows Loaded: {len(rows)}")
    print(f"Null actual_spend Rows Detected: {len(null_rows)}")
    print("-" * 80)
    if null_rows:
        print("Identified Null Rows & Reasons:")
        for idx, nr in enumerate(null_rows, start=1):
            print(f"  [{idx}] Line {nr['line_number']}: Period {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
    else:
        print("No null actual_spend rows detected.")
    print("=" * 80)
    print()

    return {
        "rows": rows,
        "null_rows": null_rows,
        "null_count": len(null_rows),
        "total_rows": len(rows)
    }


def validate_growth_request(ward: Optional[str], category: Optional[str], growth_type: Optional[str]) -> str:
    """
    Validates request constraints per agents.md:
    1. Refuses aggregation across multiple wards or categories.
    2. Requires explicit growth type; refuses guessing.
    """
    if not ward or normalize_str(ward) in PROHIBITED_AGGREGATION_KEYWORDS:
        raise ValueError(
            "REFUSAL: All-ward or aggregated ward queries are prohibited. "
            "Calculations must be performed only for an explicitly specified single ward."
        )

    if not category or normalize_str(category) in PROHIBITED_AGGREGATION_KEYWORDS:
        raise ValueError(
            "REFUSAL: All-category or aggregated category queries are prohibited. "
            "Calculations must be performed only for an explicitly specified single category."
        )

    if not growth_type or not growth_type.strip():
        raise ValueError(
            "REFUSAL: Growth type not specified. "
            "Silent formula assumption is prohibited. Please explicitly specify --growth-type (e.g. '--growth-type MoM')."
        )

    norm_gt = growth_type.strip().upper()
    if norm_gt not in SUPPORTED_GROWTH_TYPES:
        supported_keys = ", ".join(SUPPORTED_GROWTH_TYPES.keys())
        raise ValueError(
            f"REFUSAL: Unsupported growth type '{growth_type}'. "
            f"Supported growth types are: {supported_keys}."
        )

    return norm_gt


def compute_growth(
    dataset_info: Dict[str, Any],
    ward: str,
    category: str,
    growth_type: str
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Calculates growth for one explicitly requested ward and category using the
    explicitly supplied growth type and returns a per-period table with formula shown.

    Enforcement:
      - Never silently replace null actual_spend with zero.
      - If current or comparison value is null, flags the calculation.
      - Includes the exact mathematical formula alongside every row.
    """
    gt_key = validate_growth_request(ward, category, growth_type)
    formula_template = SUPPORTED_GROWTH_TYPES[gt_key]["formula"]

    all_rows = dataset_info["rows"]
    norm_req_ward = normalize_str(ward)
    norm_req_cat = normalize_str(category)

    # Filter rows strictly for requested ward and category
    matching_rows = [
        r for r in all_rows
        if normalize_str(r.get("ward")) == norm_req_ward and normalize_str(r.get("category")) == norm_req_cat
    ]

    if not matching_rows:
        available_wards = sorted(list(set(r.get("ward", "") for r in all_rows if r.get("ward"))))
        available_cats = sorted(list(set(r.get("category", "") for r in all_rows if r.get("category"))))
        raise ValueError(
            f"No data found for Ward: '{ward}', Category: '{category}'.\n"
            f"Available Wards: {available_wards}\n"
            f"Available Categories: {available_cats}"
        )

    # Sort chronologically by period
    matching_rows.sort(key=lambda r: r.get("period", ""))

    results: List[Dict[str, Any]] = []

    for i, row in enumerate(matching_rows):
        period = row.get("period", "")
        raw_ward = row.get("ward", "")
        raw_cat = row.get("category", "")
        budgeted_amount = row.get("budgeted_amount", "")
        actual_spend_str = row.get("actual_spend", "")
        row_notes = row.get("notes", "")

        result_entry: Dict[str, Any] = {
            "period": period,
            "ward": raw_ward,
            "category": raw_cat,
            "budgeted_amount": budgeted_amount,
            "actual_spend": actual_spend_str if actual_spend_str != "" else "NULL",
            "growth_type": gt_key,
            "growth_rate_pct": "",
            "formula": formula_template,
            "status": "",
            "notes": row_notes
        }

        # Check if current value is null
        if actual_spend_str == "":
            result_entry["growth_rate_pct"] = "NULL_FLAGGED"
            result_entry["status"] = "FLAGGED_NULL_CURRENT"
            flag_reason = f"Current period ({period}) actual_spend is null"
            if row_notes:
                flag_reason += f": {row_notes}"
            result_entry["notes"] = flag_reason
            results.append(result_entry)
            continue

        current_val = float(actual_spend_str)

        if gt_key == "MOM":
            if i == 0:
                # Base period has no previous month
                result_entry["growth_rate_pct"] = "N/A (Base Period)"
                result_entry["status"] = "BASE_PERIOD"
                result_entry["notes"] = row_notes or "Base period for MoM comparison"
            else:
                prev_row = matching_rows[i - 1]
                prev_period = prev_row.get("period", "")
                prev_actual_str = prev_row.get("actual_spend", "")
                prev_notes = prev_row.get("notes", "")

                # Check if comparison value is null
                if prev_actual_str == "":
                    result_entry["growth_rate_pct"] = "NULL_FLAGGED"
                    result_entry["status"] = "FLAGGED_NULL_COMPARISON"
                    comp_reason = f"Comparison period ({prev_period}) actual_spend is null"
                    if prev_notes:
                        comp_reason += f": {prev_notes}"
                    result_entry["notes"] = comp_reason
                else:
                    prev_val = float(prev_actual_str)
                    if prev_val == 0:
                        result_entry["growth_rate_pct"] = "UNDEFINED (Div by 0)"
                        result_entry["status"] = "DIV_BY_ZERO"
                    else:
                        mom_pct = ((current_val - prev_val) / prev_val) * 100.0
                        sign = "+" if mom_pct > 0 else ""
                        result_entry["growth_rate_pct"] = f"{sign}{mom_pct:.1f}%"
                        result_entry["status"] = "COMPUTED"

        results.append(result_entry)

    return results


def write_growth_output(results: List[Dict[str, Any]], output_path: str) -> None:
    """Writes computed growth results to the target CSV file."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "growth_rate_pct",
        "formula",
        "status",
        "notes"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def display_results_table(results: List[Dict[str, Any]]) -> None:
    """Displays formatted results table in console."""
    if not results:
        return

    ward = results[0]["ward"]
    category = results[0]["category"]
    growth_type = results[0]["growth_type"]
    formula = results[0]["formula"]

    print("=" * 105)
    print(f"GROWTH ANALYSIS RESULTS: {ward} | {category}")
    print(f"Growth Type: {growth_type} | Formula: {formula}")
    print("=" * 105)
    header = f"{'Period':<10} | {'Budgeted':<10} | {'Actual Spend':<14} | {'Growth Rate':<18} | {'Status':<22} | {'Notes'}"
    print(header)
    print("-" * 105)

    for r in results:
        period = r["period"]
        budget = r["budgeted_amount"]
        actual = r["actual_spend"]
        growth = r["growth_rate_pct"]
        status = r["status"]
        notes = r["notes"]
        print(f"{period:<10} | {budget:<10} | {actual:<14} | {growth:<18} | {status:<22} | {notes}")

    print("=" * 105)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator (Enforcing non-aggregation, null-flagging, explicit growth formula)."
    )
    parser.add_argument("--input", required=True, help="Path to input ward budget CSV file")
    parser.add_argument("--ward", required=True, help="Explicit ward name (aggregation prohibited)")
    parser.add_argument("--category", required=True, help="Explicit category name (aggregation prohibited)")
    parser.add_argument("--growth-type", required=True, help="Explicit growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to output growth CSV file")

    args = parser.parse_args()

    try:
        # Step 1: Load and validate dataset, reporting null rows first
        dataset_info = load_dataset(args.input)

        # Step 2: Compute growth for requested ward and category
        results = compute_growth(
            dataset_info=dataset_info,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type
        )

        # Step 3: Write results to output CSV
        write_growth_output(results, args.output)

        # Step 4: Display results table to console
        display_results_table(results)
        print(f"[SUCCESS] Growth analysis completed. Output successfully written to: {args.output}\n")

    except Exception as e:
        print(f"\n[ERROR/REFUSAL] {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
