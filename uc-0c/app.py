"""
UC-0C app.py — Strict Growth Calculator
Ensures ZERO aggregation mistakes, forces null checks, and explicitly states formula.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list[dict]:
    """Reads CSV, validates columns, intercepts null count and their specific notes."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            
        null_count = sum(1 for row in data if not row['actual_spend'].strip())
        print(f"[Dataset Loaded] {len(data)} rows. Found {null_count} actual_spend nulls.")
        return data
        
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        sys.exit(1)

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Computes growth metrics precisely scoped to ward + category, preventing aggregation.
    """
    if not ward or ward.lower() == 'any' or not category or category.lower() == 'any':
        raise ValueError("REFUSED: Aggregation across multiple wards or categories disabled per compliance rules.")
        
    if not growth_type:
        raise ValueError("REFUSED: --growth-type MUST be explicitly specified (e.g., MoM). No guessing allowed.")

    # Filter data strictly to this ward/category context
    scoped_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort strictly by period (YYYY-MM)
    scoped_data.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, current in enumerate(scoped_data):
        period = current['period']
        curr_spend_str = current['actual_spend'].strip()
        
        # Rule 2: Flag Nulls explicitely from notes
        if not curr_spend_str:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'MoM Growth': f"Must be flagged — not computed (Reason: {current['notes']})"
            })
            continue
            
        curr_val = float(curr_spend_str)
        
        # We need a previous value depending on growth_type
        # MoM = i-1
        # YoY = 12 months prior (not applicable for MoM focus, but building structure)
        
        if growth_type.upper() == 'MOM':
            if i == 0:
                results.append({
                    'Ward': ward,
                    'Category': category,
                    'Period': period,
                    'Actual Spend (₹ lakh)': curr_val,
                    'MoM Growth': "N/A (First Period)"
                })
                continue
                
            prev = scoped_data[i-1]
            prev_spend_str = prev['actual_spend'].strip()
            
            if not prev_spend_str:
                results.append({
                    'Ward': ward,
                    'Category': category,
                    'Period': period,
                    'Actual Spend (₹ lakh)': curr_val,
                    'MoM Growth': "N/A (Previous Period was NULL)"
                })
                continue
                
            prev_val = float(prev_spend_str)
            if prev_val == 0:
                growth_str = "Div by Zero"
            else:
                growth_pct = ((curr_val - prev_val) / prev_val) * 100
                prefix = "+" if growth_pct > 0 else ""
                # Rule 3: Show formula used in every output row
                growth_str = f"{prefix}{growth_pct:.1f}% [Formula: ({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}]"
                
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': curr_val,
                'MoM Growth': growth_str
            })
            
        else:
            raise ValueError(f"REFUSED: Supported formula type '{growth_type}' not fully implemented.")
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Strict Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Strict Ward context filter")
    parser.add_argument("--category", required=True, help="Strict Category filter")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY explicitly")
    parser.add_argument("--output", required=True, help="Path to write table")
    
    try:
        args = parser.parse_args()
    except:
        # If arguments are missing, arg parser will fail out naturally, but let's emulate strict refusing
        print("REFUSED: Missing explicit parameters. Never aggregate or guess.")
        sys.exit(1)
        
    try:
        data = load_dataset(args.input)
        table = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write to Output CSV
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'MoM Growth'])
            writer.writeheader()
            for row in table:
                writer.writerow(row)
                
        print(f"\nSuccess. Computed metrics written safely to {args.output}")
        
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
