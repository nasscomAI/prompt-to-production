"""
UC-0C — Number That Looks Right
Reads ward_budget.csv and produces growth_output.csv.
RICE & CRAFT enforcement:
- Single ward & category filtering only (refuse cross-ward/category aggregations)
- Explicit null handling (flag rows, report notes, do not fill with 0)
- Include exact formula used in output
- Refuse execution if --growth-type is missing or invalid
"""
import argparse
import csv
import os
import sys
from typing import Dict, List, Tuple


def load_dataset(path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Skill 1: load_dataset
    Reads CSV, validates required columns, and identifies null actual_spend rows.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Budget dataset file not found: {path}")

    rows: List[Dict[str, str]] = []
    null_rows: List[Dict[str, str]] = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Missing required columns in dataset. Expected: {required_cols}")

        for row in reader:
            rows.append(row)
            actual_val = row.get("actual_spend", "").strip()
            if not actual_val:
                null_rows.append(row)

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str
) -> List[Dict[str, str]]:
    """Skill 2: compute_growth
    Filters dataset by ward and category, calculates sequential MoM/YoY growth percentage,
    documents exact formula used, and preserves null notes without silent zero substitution.
    """
    # Validation / Refusal Logic
    if not ward or ward.lower() == "all" or not category or category.lower() == "all":
        print("Refusal: All-ward or cross-category aggregation is prohibited. Please specify exact --ward and --category.", file=sys.stderr)
        sys.exit(1)

    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        print(f"Refusal: Invalid or missing growth type '{growth_type}'. Specify --growth-type MoM or YoY.", file=sys.stderr)
        sys.exit(1)

    # Filter rows by ward and category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip().lower() == ward.strip().lower()
        and r.get("category", "").strip().lower() == category.strip().lower()
    ]

    if not filtered:
        print(f"Error: No matching records found for Ward '{ward}' and Category '{category}'.", file=sys.stderr)
        sys.exit(1)

    # Sort sequentially by period
    filtered.sort(key=lambda r: r.get("period", ""))

    output_rows: List[Dict[str, str]] = []

    for idx, row in enumerate(filtered):
        period = row.get("period", "")
        w = row.get("ward", "")
        cat = row.get("category", "")
        budgeted = row.get("budgeted_amount", "")
        actual_str = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        # Handle Current Null Row
        if not actual_str:
            output_rows.append({
                "period": period,
                "ward": w,
                "category": cat,
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth_pct": "NULL",
                "formula": f"NULL — {notes}" if notes else "NULL — Data missing",
                "notes": notes,
            })
            continue

        actual_val = float(actual_str)

        # Baseline Row (First Period)
        if idx == 0:
            output_rows.append({
                "period": period,
                "ward": w,
                "category": cat,
                "budgeted_amount": budgeted,
                "actual_spend": f"{actual_val:.1f}" if actual_val != int(actual_val) else f"{int(actual_val)}",
                "growth_pct": "N/A",
                "formula": "Initial period — baseline",
                "notes": notes,
            })
            continue

        # Sequential MoM / YoY Calculation
        prev_row = filtered[idx - 1]
        prev_actual_str = prev_row.get("actual_spend", "").strip()

        if not prev_actual_str:
            output_rows.append({
                "period": period,
                "ward": w,
                "category": cat,
                "budgeted_amount": budgeted,
                "actual_spend": f"{actual_val:.1f}" if actual_val != int(actual_val) else f"{int(actual_val)}",
                "growth_pct": "NULL",
                "formula": f"Previous period ({prev_row.get('period', '')}) spend is NULL — cannot compute growth",
                "notes": notes,
            })
            continue

        prev_actual_val = float(prev_actual_str)
        if prev_actual_val == 0:
            growth_str = "N/A"
            formula_str = "Previous period spend is zero"
        else:
            diff = actual_val - prev_actual_val
            pct = (diff / prev_actual_val) * 100.0
            sign = "+" if pct > 0 else ""
            growth_str = f"{sign}{pct:.1f}%"
            formula_str = "(actual_spend - prev_spend) / prev_spend * 100"

        output_rows.append({
            "period": period,
            "ward": w,
            "category": cat,
            "budgeted_amount": budgeted,
            "actual_spend": f"{actual_val:.1f}" if actual_val != int(actual_val) else f"{int(actual_val)}",
            "growth_pct": growth_str,
            "formula": formula_str,
            "notes": notes,
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth type metric: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")

    args = parser.parse_args()

    # Enforcement: Refuse if mandatory options are missing
    if not args.ward or not args.category:
        print("Refusal: --ward and --category parameters are required. Cross-ward aggregation is not permitted.", file=sys.stderr)
        sys.exit(1)

    if not args.growth_type:
        print("Refusal: --growth-type option is required (MoM or YoY).", file=sys.stderr)
        sys.exit(1)

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Info: Loaded {len(rows)} records. Detected {len(null_rows)} deliberate null actual_spend rows.")

    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Growth calculation complete. Output written to {args.output}")


if __name__ == "__main__":
    main()