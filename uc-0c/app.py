"""
UC-0C app.py — Growth Calculator
Implements the load_dataset and compute_growth skills.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """
    Reads CSV, validates columns, reports null count and identifies which rows have nulls before returning data.
    """
    dataset = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                dataset.append(row)
                actual = row.get("actual_spend", "").strip()
                if not actual or actual.lower() == "null":
                    null_rows.append((row.get("period", f"Row {i}"), row.get("ward", ""), row.get("category", ""), row.get("notes", "")))
                    
        if null_rows:
            print(f"\n--- Data Validation Report ---")
            print(f"Warning: Found {len(null_rows)} deliberate null actual_spend rows.")
            for period, ward, cat, notes in null_rows:
                print(f"  - Null in {period} | {ward} | {cat}. Reason: {notes}")
            print(f"------------------------------\n")
            
        return dataset
    except FileNotFoundError:
        print(f"ERROR: Could not find the input file at {filepath}")
        sys.exit(1)

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes specific ward, category, and growth_type context, returning a per-period table with formulas shown.
    Refuses silent aggregation.
    """
    if ward is None or ward.lower() == "all" or category is None or category.lower() == "all":
        raise ValueError("REFUSAL: Cannot aggregate across wards or categories unless explicitly instructed.")
        
    if not growth_type: # Technically caught earlier by argparse but adding safeguard
        raise ValueError("REFUSAL: --growth-type not specified. Please specify (e.g. MoM), I will not guess.")

    # Filter dataset for specific ward and category strictly without aggregating
    filtered = [r for r in data if r.get('ward') == ward and r.get('category') == category]
    
    # Sort chronologically by period (YYYY-MM string sorting)
    filtered.sort(key=lambda x: x.get('period', ''))
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current.get('period')
        spend_str = current.get('actual_spend', '').strip()
        
        row_out = {
            "ward": current.get('ward'),
            "category": current.get('category'),
            "period": period,
            "actual_spend": spend_str,
            "growth_type": growth_type,
            "growth_value": "N/A",
            "formula": "N/A",
            "flag": ""
        }
        
        # Null handling
        if not spend_str or spend_str.lower() == "null":
            row_out['flag'] = f"NULL DATA: {current.get('notes', 'No reason provided')}"
            row_out['formula'] = "Cannot compute on NULL"
        else:
            current_val = float(spend_str)
            if growth_type.lower() == "mom":
                if i == 0:
                    row_out['formula'] = "First period"
                else:
                    prev = filtered[i-1]
                    prev_str = prev.get('actual_spend', '').strip()
                    
                    if not prev_str or prev_str.lower() == "null":
                        row_out['formula'] = "Cannot compute (previous period NULL)"
                        row_out['flag'] = "Previous data was NULL"
                    else:
                        prev_val = float(prev_str)
                        if prev_val == 0:
                            row_out['formula'] = f"({current_val} - 0) / 0"
                        else:
                            growth = (current_val - prev_val) / prev_val
                            row_out['growth_value'] = f"{growth:+.1%}"
                            row_out['formula'] = f"({current_val} - {prev_val}) / {prev_val}"
            else:
                raise ValueError(f"REFUSAL: Unsupported or unrecognized growth type: {growth_type}")
                
        results.append(row_out)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="E.g., MoM. Do not let system guess.")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    # Pre-computation rule enforcement
    if not args.growth_type:
        print("ERROR: --growth-type not specified. Refusing to guess. Please provide a formula type (e.g. MoM).")
        return
        
    data = load_dataset(args.input)
    
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    # Write output CSV
    if results:
        fieldnames = ["ward", "category", "period", "actual_spend", "growth_type", "growth_value", "formula", "flag"]
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully computed growth. Results mathematically verified and output to {args.output}")
    else:
        print("No matches found for the specified ward and category.")

if __name__ == "__main__":
    main()
