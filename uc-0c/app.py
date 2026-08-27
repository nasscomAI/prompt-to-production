"""
UC-0C app.py — Number That Looks Right.
Implements MoM/YoY growth analysis with strict data integrity and null handling.
Uses standard libraries (csv, argparse) for maximum compatibility.
"""
import csv
import argparse
import os
import sys
from datetime import datetime

def load_dataset(file_path):
    """
    Reads CSV, validates columns, and reports null spend rows.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: Input file not found at {file_path}")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        sys.exit(1)
            
    if not data:
        print("ERROR: CSV is empty or invalid.")
        sys.exit(1)
        
    # Validate columns
    required = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    missing = [col for col in required if col not in data[0]]
    if missing:
        print(f"ERROR: Missing mandatory columns: {', '.join(missing)}")
        sys.exit(1)
        
    # Flag null rows explicitly as per enforcement rules
    print("--- DATA INTEGRITY REPORT ---")
    null_count = 0
    for row in data:
        spend = row['actual_spend'].strip()
        if not spend or spend.lower() == 'null' or spend == '':
            null_count += 1
            print(f"FLAGGED NULL: {row['period']} | {row['ward']} | {row['category']} | Reason: {row['notes']}")
    
    if null_count > 0:
        print(f"Total FLAGGED NULL values: {null_count}")
    else:
        print("No NULL values found in actual_spend.")
    print("-----------------------------\n")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates growth while strictly avoiding unauthorized aggregation.
    """
    if not growth_type:
        print("ERROR: --growth-type (MoM or YoY) is mandatory. Refusing to guess.")
        sys.exit(1)
        
    # Filter to specific ward and category - NO AGGREGATION
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"ERROR: No data found for Ward '{ward}' and Category '{category}'.")
        sys.exit(1)
        
    # Sort by period for correct growth calculation
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        spend_str = row['actual_spend'].strip()
        
        # Parse spend
        try:
            actual = float(spend_str) if spend_str and spend_str.lower() != 'null' else None
        except ValueError:
            actual = None
            
        growth_val_str = "n/a"
        formula = "N/A"
        
        if actual is None:
            growth_val_str = "NULL"
            formula = f"Refused: {row['notes']}"
        else:
            if growth_type == "MoM":
                if i > 0:
                    prev_row = filtered[i-1]
                    prev_spend_str = prev_row['actual_spend'].strip()
                    try:
                        prev_val = float(prev_spend_str) if prev_spend_str and prev_spend_str.lower() != 'null' else None
                    except ValueError:
                        prev_val = None
                        
                    if prev_val is None:
                        growth_val_str = "n/a"
                        formula = f"Cannot compute: Previous period ({prev_row['period']}) is NULL"
                    else:
                        growth_pct = ((actual - prev_val) / prev_val) * 100
                        growth_val_str = f"{growth_pct:+.1f}%"
                        formula = f"(({actual} - {prev_val}) / {prev_val}) * 100"
                else:
                    formula = "Initial period - no prior data"
            
            elif growth_type == "YoY":
                try:
                    curr_date = datetime.strptime(period, "%Y-%m")
                    prev_year_str = f"{curr_date.year - 1}-{curr_date.month:02d}"
                    
                    prev_year_row = next((r for r in filtered if r['period'] == prev_year_str), None)
                    
                    if prev_year_row:
                        prev_spend_str = prev_year_row['actual_spend'].strip()
                        try:
                            prev_val = float(prev_spend_str) if prev_spend_str and prev_spend_str.lower() != 'null' else None
                        except ValueError:
                            prev_val = None
                            
                        if prev_val is None:
                            growth_val_str = "n/a"
                            formula = f"Cannot compute: Same period last year ({prev_year_str}) is NULL"
                        else:
                            growth_pct = ((actual - prev_val) / prev_val) * 100
                            growth_val_str = f"{growth_pct:+.1f}%"
                            formula = f"(({actual} - {prev_val}) / {prev_val}) * 100"
                    else:
                        formula = f"No data found for {prev_year_str}"
                except ValueError:
                    formula = "Invalid date format"

        results.append({
            "Ward": row['ward'],
            "Category": row['category'],
            "Period": period,
            "Actual Spend": "NULL" if actual is None else actual,
            "Growth": growth_val_str,
            "Formula": formula
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=True, help="Target Ward")
    parser.add_argument("--category", required=True, help="Target Category")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Calculation type")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()
    
    # 1. Load and Validate
    data = load_dataset(args.input)
    
    # 2. Compute Growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # 3. Save Output
    if results:
        keys = results[0].keys()
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            print(f"SUCCESS: Analysis complete. Results saved to {args.output}")
            
            # Print sample output
            print("\nFinal Results Table:")
            # Simple column alignment for display
            col_widths = {k: max(len(k), max(len(str(r[k])) for r in results)) for k in keys}
            header = " | ".join(k.ljust(col_widths[k]) for k in keys)
            print(header)
            print("-" * len(header))
            for res in results:
                print(" | ".join(str(res[k]).ljust(col_widths[k]) for k in keys))
        except Exception as e:
            print(f"ERROR: Failed to write output: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
