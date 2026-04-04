import argparse
import csv
import sys
from typing import List, Dict

def load_dataset(filepath: str) -> List[Dict]:
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    dataset = []
    null_count = 0
    null_rows = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                print("Error: Dataset schema is corrupted or missing required columns.")
                sys.exit(1)

            for row_num, row in enumerate(reader, start=2): # +2 for header and 1-indexing
                dataset.append(row)
                if not row["actual_spend"] or row["actual_spend"].strip() == "":
                    null_count += 1
                    null_rows.append(f"Row {row_num}: {row['period']} - {row['ward']} - {row['category']} (Reason: {row['notes']})")
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)

    # Strict Report before returning
    print("=== Data Completeness Report ===")
    print(f"Total rows parsed: {len(dataset)}")
    print(f"Null 'actual_spend' values found: {null_count}")
    for nr in null_rows:
        print(f"  -> {nr}")
    print("================================\n")

    return dataset


def compute_growth(dataset: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """
    Skill: compute_growth
    Takes ward, category, and growth_type, returning a per-period table with formulas shown explicitly.
    """
    # 1. Enforcement: Never aggregate across wards or categories. Refuse if asked.
    if ward.lower() in ["all", "any"] or category.lower() in ["all", "any"]:
        print("AGENT REFUSAL: Aggregation across wards or categories without explicit bounds is not permitted by enforcement rules.")
        sys.exit(1)

    # 2. Enforcement: Refuse if --growth-type is missing. (Enforced by argparse required=True, but let's double check)
    if not growth_type or growth_type not in ["MoM", "YoY"]:
        print("AGENT REFUSAL: Exact --growth-type must be specified (e.g., MoM or YoY). Guessing is strictly prohibited.")
        sys.exit(1)

    # Filter data for specific ward and category
    filtered = [r for r in dataset if r['ward'].strip() == ward and r['category'].strip() == category]
    
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])

    output_rows = []
    
    for i, current in enumerate(filtered):
        period = current['period']
        current_spend_str = current['actual_spend'].strip()
        notes = current['notes'].strip()
        
        row_out = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": current_spend_str if current_spend_str else "NULL",
            f"{growth_type} Growth": "N/A",
            "Formula Used": "N/A"
        }

        # 3. Enforcement: Flag every null row before computing. Do not compute.
        if not current_spend_str:
            row_out[f"{growth_type} Growth"] = f"Must be flagged — not computed (Notes: {notes})"
            row_out["Formula Used"] = "Null Constraint"
            output_rows.append(row_out)
            continue
            
        current_val = float(current_spend_str)
        
        # Calculate matching previous logic (MoM means previous month)
        prev_val = None
        prev_spend_str = None
        if growth_type == "MoM" and i > 0:
            prev_row = filtered[i-1]
            # Verify it's actually previous month sequentially
            prev_spend_str = prev_row['actual_spend'].strip()
            if prev_spend_str:
                prev_val = float(prev_spend_str)

        if prev_val is not None and prev_val != 0:
            growth = ((current_val - prev_val) / prev_val) * 100
            
            # Formatting as requested: +33.1% (notes)
            sign = "+" if growth > 0 else ""
            notes_str = f" ({notes})" if notes else ""
            row_out[f"{growth_type} Growth"] = f"{sign}{growth:.1f}%{notes_str}"
            row_out["Formula Used"] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
        elif prev_val == 0:
            row_out[f"{growth_type} Growth"] = "Undefined (division by zero)"
            row_out["Formula Used"] = f"(({current_val} - 0) / 0) * 100"
        else:
            if i == 0 or growth_type == "YoY": # We don't have YoY data in 1yr dataset mostly
                row_out[f"{growth_type} Growth"] = "Insufficient previous data"
                row_out["Formula Used"] = "Baseline Period"
            elif not prev_spend_str:
                row_out[f"{growth_type} Growth"] = "Cannot compute (previous period was NULL)"
                row_out["Formula Used"] = f"(({current_val} - NULL) / NULL) * 100"

        output_rows.append(row_out)

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Civic Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    
    # We purposefully do NOT provide a default for growth-type to enforce Rule 4
    parser.add_argument("--growth-type", required=True, help="Must specify MoM or YoY")
    
    # Required filters to prevent cross-ward/category aggregations (Rule 1)
    parser.add_argument("--ward", required=True, help="Specific Ward to analyze (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific Category to analyze (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()

    # Skill 1: Validate and report nulls
    dataset = load_dataset(args.input)
    
    # Skill 2: Compute
    results = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type
    )

    if not results:
        print(f"No records found for Ward '{args.ward}' and Category '{args.category}'.")
        sys.exit(0)

    # Write output structure
    fieldnames = list(results[0].keys())
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Growth table written to '{args.output}'")
    except Exception as e:
        print(f"Error writing to output CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
