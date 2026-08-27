"""
UC-0C app.py
Implemented using strict local python calculation logic to adhere to anti-aggregation, strict null-checking, and formula explicitness rules.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list[dict]:
    """
    Reads CSV, validates columns, and reports null count along with which rows contain nulls before returning.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
    except Exception as e:
        raise RuntimeError(f"Critical Error: Failed to read budget file. {e}")
        
    null_rows = []
    
    # Flag every null row before computing
    for i, row in enumerate(data):
        if not row.get('actual_spend') or row.get('actual_spend').strip() == '':
            notes = row.get('notes', 'No notes provided')
            null_rows.append(row)
            print(f"WARNING: Null value detected in actual_spend. Row period: {row.get('period')}, Ward: {row.get('ward')}, Category: {row.get('category')}. Reason: {notes}")
            
    print(f"Dataset loaded. Total rows: {len(data)}. Null rows flagged: {len(null_rows)}\n")
    return data

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Takes ward, category, and growth_type to return a per-period calculation table.
    """
    if not ward or not category:
        raise ValueError("CRITICAL: Never aggregate across wards or categories. You must specify both --ward and --category.")
        
    if not growth_type:
        raise ValueError("CRITICAL: --growth-type not specified. Refusing to guess formula.")
        
    if growth_type.upper() != "MOM":
        raise ValueError(f"CRITICAL: Unrecognized growth type {growth_type}. Only MoM supported currently.")

    # Filter for the exact requested ward and category (anti-aggregation enforcement)
    filtered = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    
    # Sort strictly by period
    filtered.sort(key=lambda x: x.get('period', ''))
    
    results = []
    
    for i in range(len(filtered)):
        current_row = filtered[i]
        period = current_row.get('period')
        
        current_val_str = current_row.get('actual_spend', '').strip()
        
        if not current_val_str:
            # Current row is null
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (\u20b9 lakh)": "NULL",
                "MoM Growth": "NULL (not computed due to current missing data)"
            })
            continue
            
        current_val = float(current_val_str)
        
        if i == 0:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (\u20b9 lakh)": str(current_val),
                "MoM Growth": "N/A (first period)"
            })
            continue
            
        prev_row = filtered[i - 1]
        prev_val_str = prev_row.get('actual_spend', '').strip()
        
        if not prev_val_str:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (\u20b9 lakh)": str(current_val),
                "MoM Growth": "NULL (not computed due to previous missing data)"
            })
            continue
            
        prev_val = float(prev_val_str)
        
        # Calculate MoM Growth strictly
        if prev_val == 0:
            growth_pct = 0.0
            formula = f"({current_val} / {prev_val} - 1) [Div by Zero]"
            growth_str = f"NaN% [Formula: {formula}]"
        else:
            growth_pct = ((current_val / prev_val) - 1.0) * 100
            sign = "+" if growth_pct > 0 else ""
            formula = f"({current_val} / {prev_val} - 1) * 100"
            growth_str = f"{sign}{growth_pct:.1f}% [Formula: {formula}]"
            
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (\u20b9 lakh)": str(current_val),
            "MoM Growth": growth_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name (required to prevent aggregation)")
    parser.add_argument("--category", required=False, help="Category name (required to prevent aggregation)")
    parser.add_argument("--growth-type", required=False, help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    try:
        print("Loading dataset and running null checks...")
        dataset = load_dataset(args.input)
        
        print(f"Computing growth metrics for Ward: '{args.ward}', Category: '{args.category}'...")
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if results:
            fieldnames = ["Ward", "Category", "Period", "Actual Spend (\u20b9 lakh)", "MoM Growth"]
            with open(args.output, 'w', encoding='utf-8', newline='') as out:
                writer = csv.DictWriter(out, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
                
            print(f"\nDone. Results written to {args.output}")
        else:
            print("\nNo matching records found for that ward and category.")
            
    except Exception as e:
        print(f"\nExecution Refused: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
