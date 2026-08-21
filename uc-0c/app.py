import argparse
import csv
import sys
from typing import List, Dict, Tuple, Optional

def load_dataset(filepath: str) -> Tuple[List[Dict], List[Dict]]:
    """Reads a CSV file, validates its columns, and reports null values."""
    data = []
    nulls = []
    expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not expected_cols.issubset(set(reader.fieldnames or [])):
                raise Exception(f"Missing expected columns. Found: {reader.fieldnames}")
                
            for row_num, row in enumerate(reader, start=2): # 1-based index including header
                data.append(row)
                
                # Check for empty actual_spend
                val = row['actual_spend'].strip()
                if not val:
                    nulls.append(row)
                    
        print(f"Loaded {len(data)} rows.")
        if nulls:
            print(f"WARNING: Detected {len(nulls)} null rows in 'actual_spend' before computation.")
            for n in nulls:
                print(f"  - {n['period']} | {n['ward']} | {n['category']} -> Note: {n['notes']}")
                
        return data, nulls
    except Exception as e:
        raise Exception(f"Failed to load dataset: {e}")

def compute_growth(data: List[Dict], ward: str, category: str, growth_type: str) -> List[Dict]:
    """Calculates row-by-row growth for specific ward/category."""
    
    if not ward or not category:
        raise ValueError("REFUSED: Never aggregate across wards or categories unless explicitly instructed.")
        
    if growth_type.lower() != "mom":
        raise ValueError(f"REFUSED: Unhandled growth-type '{growth_type}'. Cannot guess formula.")
        
    # Filter dataset strictly
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort chronologically just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    prev_period = None
    
    for row in filtered:
        out_row = {
            'Ward': row['ward'],
            'Category': row['category'],
            'Period': row['period'],
        }
        
        spend_str = row['actual_spend'].strip()
        current_spend = None
        if spend_str:
            try:
                current_spend = float(spend_str)
            except ValueError:
                current_spend = None
                
        out_row['Actual Spend (lakh)'] = current_spend if current_spend is not None else "NULL"
        
        if current_spend is None:
            # Must flag — not computed
            out_row['Growth'] = "FLAGGED"
            out_row['Formula'] = f"Missing data: {row['notes']}"
            prev_spend = None # Reset for next period
            prev_period = row['period']
            results.append(out_row)
            continue
            
        if prev_spend is None:
            # First row with data or previous row was null
            out_row['Growth'] = "N/A"
            if prev_period is None:
                out_row['Formula'] = "First reporting period"
            else:
                out_row['Formula'] = "Previous period was NULL"
        else:
            # Compute MoM
            diff = current_spend - prev_spend
            growth_pct = (diff / prev_spend) * 100
            
            # Formatting nicely
            sign = "+" if growth_pct > 0 else ""
            out_row['Growth'] = f"{sign}{growth_pct:.1f}%"
            out_row['Formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            
        prev_spend = current_spend
        prev_period = row['period']
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Must specify ward")
    parser.add_argument("--category", required=True, help="Must specify category")
    parser.add_argument("--growth-type", required=True, help="E.g., MoM")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    try:
        data, nulls = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if results:
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend (lakh)', 'Growth', 'Formula'])
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully computed growth and wrote {len(results)} rows to {args.output}")
        else:
            print("No data matched the provided ward and category.")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
