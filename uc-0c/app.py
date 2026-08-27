"""
UC-0C app.py — Number That Looks Right
Implements load_dataset and compute_growth skills as defined in
agents.md (RICE enforcement) and skills.md (I/O contracts).
"""
import argparse
import csv
import os
import sys
from typing import List, Dict, Optional


def load_dataset(input_path: str) -> List[Dict]:
    """
    Skill: load_dataset
    Reads the CSV, validates that all required columns are present,
    and returns a list of dictionaries.
    Before returning, flags all null actual_spend rows to standard error
    along with the reason from the notes column.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows: List[Dict] = []

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or invalid.")
        
        fieldnames = set(reader.fieldnames)
        if not required_columns.issubset(fieldnames):
            missing = required_columns - fieldnames
            raise ValueError(f"Missing required columns in CSV: {missing}")

        for i, row in enumerate(reader, start=1):
            # Parse numeric values
            try:
                budgeted_amount = float(row["budgeted_amount"]) if row["budgeted_amount"].strip() else 0.0
            except ValueError:
                print(f"[WARN] Line {i}: non-numeric budgeted_amount '{row['budgeted_amount']}' default to 0.0", file=sys.stderr)
                budgeted_amount = 0.0

            actual_spend_str = row["actual_spend"].strip()
            actual_spend: Optional[float] = None
            if actual_spend_str:
                try:
                    actual_spend = float(actual_spend_str)
                except ValueError:
                    print(f"[WARN] Line {i}: non-numeric actual_spend '{actual_spend_str}' treated as null", file=sys.stderr)
                    actual_spend = None

            rows.append({
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": row["notes"].strip()
            })

    # Flag all null rows
    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"[INFO] Found {len(null_rows)} null actual_spend rows in dataset:", file=sys.stderr)
    for nr in null_rows:
        print(f"  - [NULL FLAG] Period: {nr['period']} | Ward: {nr['ward']} | Category: {nr['category']} | Reason: {nr['notes'] or 'None specified'}", file=sys.stderr)

    return rows


def compute_growth(dataset: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Skill: compute_growth
    Computes MoM growth for the specified ward and category.
    Includes formula in every output row.
    Refuses if multiple wards or categories are requested (no aggregation allowed).
    Refuses if growth_type is not MoM.
    """
    if not growth_type:
        raise ValueError("Growth type not specified. System refuses to guess.")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth-type '{growth_type}'. Only 'MoM' is supported.")

    if not ward or ward.lower() == "any" or ward.lower() == "all":
        raise ValueError("Refusing calculation: Aggregation across multiple wards is prohibited.")
    if not category or category.lower() == "any" or category.lower() == "all":
        raise ValueError("Refusing calculation: Aggregation across multiple categories is prohibited.")

    # Filter data strictly by ward and category
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]

    if not filtered:
        raise ValueError(f"No data found matching Ward: '{ward}' and Category: '{category}'.")

    # Sort strictly by period (YYYY-MM)
    filtered.sort(key=lambda r: r["period"])

    output_rows: List[Dict] = []
    for i, current in enumerate(filtered):
        period = current["period"]
        actual_spend = current["actual_spend"]
        
        # If current actual_spend is null
        if actual_spend is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": f"N/A - actual spend is null (Reason: {current['notes']})"
            })
            continue

        # If it's the first period
        if i == 0:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual_spend:.1f}",
                "growth": "NULL",
                "formula": "N/A - first period in dataset"
            })
            continue

        # Get previous row
        previous = filtered[i - 1]
        prev_actual_spend = previous["actual_spend"]

        # If previous actual_spend is null
        if prev_actual_spend is None:
            output_rows.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual_spend:.1f}",
                "growth": "NULL",
                "formula": f"N/A - previous period actual spend is null (Reason: {previous['notes']})"
            })
            continue

        # Compute MoM growth
        # Growth = ((Current - Previous) / Previous) * 100
        diff = actual_spend - prev_actual_spend
        growth_pct = (diff / prev_actual_spend) * 100
        
        # Format the percentage growth with + sign for positive values
        sign = "+" if growth_pct > 0 else ""
        # Handle exact zero
        if abs(growth_pct) < 1e-9:
            growth_str = "0.0%"
        else:
            growth_str = f"{sign}{growth_pct:.1f}%"

        formula_str = f"({actual_spend:.1f} - {prev_actual_spend:.1f}) / {prev_actual_spend:.1f}"

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": f"{actual_spend:.1f}",
            "growth": growth_str,
            "formula": formula_str
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    # Enforcement: if growth-type is not specified, refuse and exit
    if not args.growth_type:
        print("[ERROR] Refusal: --growth-type must be specified.", file=sys.stderr)
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        # Write output file
        with open(args.output, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
            writer.writeheader()
            writer.writerows(results)

        print(f"[INFO] Growth calculation complete. Output written to {args.output}", file=sys.stderr)
    except ValueError as e:
        print(f"[ERROR] Refusal condition met: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
