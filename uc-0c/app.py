"""
UC-0C app.py — Growth Metric Calculator
Built using the capabilities and properties defined in agents.md and skills.md.
"""
import argparse
import csv
import sys
from typing import List, Dict

def load_dataset(filepath: str) -> List[Dict]:
    """Reads CSV, validates columns, reports null count and which rows."""
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data: List[Dict] = []
    null_count: int = 0
    null_rows: List[tuple] = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Handle potential BOM in the file
            reader = csv.DictReader(f)
            fn_list = reader.fieldnames
            if fn_list is None:
                fn_list = []
            header = {col.strip().lstrip('\ufeff') for col in fn_list if col}
            
            # Since some fieldnames might not exactly match our expectations due to trailing spaces
            # We'll normalize keys.
            def normalize_row(r: Dict[str, str]) -> Dict[str, str]:
                return {k.strip().lstrip('\ufeff'): str(v).strip() for k, v in r.items() if k and v is not None}

            if not required_cols.issubset(header):
                raise ValueError(f"Missing required columns. Expected: {required_cols}, found: {header}")
                
            for row_raw in reader:
                safe_row = dict(row_raw) # type: ignore
                row = normalize_row(safe_row)
                val = row.get('actual_spend', '')
                if not val:
                    null_count += 1 # type: ignore
                    null_rows.append((row.get('period'), row.get('ward'), row.get('category'), row.get('notes', 'No reason given')))
                data.append(row)
                
    except FileNotFoundError:
        print(f"Error: Dataset not found at {filepath}")
        sys.exit(1)
        
    print(f"Dataset Loaded. Found {null_count} null actual_spend rows.")
    for nr in null_rows:
        print(f" - NULL FLAG: Period={nr[0]}, Ward={nr[1]}, Category={nr[2]}, Reason: {nr[3]}")
        
    return data

def compute_growth(data: List[Dict], target_ward: str, target_category: str, growth_type: str) -> List[Dict]:
    """Calculates precise growth metrics for a specific ward and category."""
    if not target_ward or not target_category or target_ward.lower() == "any" or target_category.lower() == "any":
        print("REFUSAL: Cannot aggregate across multiple wards or categories. Target ward and category must be explicitly specified.")
        sys.exit(1)
        
    # filter data
    filtered = [d for d in data if d.get('ward') == target_ward and d.get('category') == target_category]
    
    if not filtered:
        print(f"Warning: No data matching Ward='{target_ward}' and Category='{target_category}'. Check exact string matches.")
        sys.exit(0)
    
    # sort by period as it's typically YYYY-MM
    filtered.sort(key=lambda x: x.get('period', ''))
    
    output = []
    prev_spend = None
    
    if growth_type.upper() != "MOM":
        print(f"REFUSAL: Unsupported growth type '{growth_type}'. Currently only MoM is supported.")
        sys.exit(1)
        
    for i, row in enumerate(filtered):
        period = row.get('period', '')
        notes = row.get('notes', '')
        val_str = row.get('actual_spend', '')
        
        out_row = {
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend': val_str if val_str else 'NULL',
        }
        
        if not val_str:
            out_row['MoM Growth'] = 'NULL'
            out_row['Growth Formula'] = f"Cannot compute: actual_spend is NULL"
            out_row['Notes'] = f"Null reason: {notes}" if notes else "Null reason: Not provided"
            # Can't calculate next month sequentially if the prior month was null
            prev_spend = None 
        else:
            try:
                current_spend = float(val_str)
            except ValueError:
                # Value is present but not float parseable
                out_row['MoM Growth'] = 'NULL'
                out_row['Growth Formula'] = f"Cannot compute: Invalid actual_spend value '{val_str}'"
                out_row['Notes'] = notes
                prev_spend = None
                output.append(out_row)
                continue
            
            if prev_spend is None:
                out_row['MoM Growth'] = 'n/a'
                out_row['Growth Formula'] = 'n/a (first valid period or prev was null)'
                out_row['Notes'] = notes
            else:
                if prev_spend == 0:
                    growth_pct = 0.0
                    formula = f"({current_spend} - 0) / 0"
                else:
                    growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                    formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                
                sign = "+" if growth_pct > 0 else ""
                out_row['MoM Growth'] = f"{sign}{growth_pct:.1f}%"
                out_row['Growth Formula'] = formula
                out_row['Notes'] = notes
                
            prev_spend = current_spend
            
        output.append(out_row)
        
    return output

def main():
    parser = argparse.ArgumentParser(description="Calculate departmental budget growth per ward and category.")
    parser.add_argument("--input", required=True, help="Input CSV dataset path")
    parser.add_argument("--ward", required=True, help="Target ward name")
    parser.add_argument("--category", required=True, help="Target category name")
    # Make growth_type optional to trigger explicit refusal in logic
    parser.add_argument("--growth-type", required=False, help="Growth type to calculate (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()
    
    # ENFORCEMENT: Never guess if growth-type is omitted
    if not args.growth_type:
        print("REFUSAL: --growth-type was not specified. I will not guess the growth type. Please provide it.")
        sys.exit(1)

    # 1. Load dataset
    data = load_dataset(args.input)
    
    # 2. Compute Growth explicitly per Ward & Category
    result = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # 3. Output payload
    if result:
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend', 'MoM Growth', 'Growth Formula', 'Notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result)
            print(f"Success: Analysis written to {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
