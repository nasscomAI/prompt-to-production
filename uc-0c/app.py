import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            if not row.get('actual_spend') or row['actual_spend'].strip() == '':
                null_rows.append(row)
                
    # Report null count and reasons transparently
    if null_rows:
        print(f"FLAG: Found {len(null_rows)} null actual_spend values in the dataset:")
        for r in null_rows:
            print(f" - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    # Enforcement 1: Never aggregate across wards or categories
    if not ward or ward.lower() == 'all' or ward.lower() == 'any':
        raise ValueError("REFUSED: Aggregation across multiple wards is explicitly forbidden. Please specify a single ward.")
    if not category or category.lower() == 'all' or category.lower() == 'any':
        raise ValueError("REFUSED: Aggregation across multiple categories is explicitly forbidden. Please specify a single category.")
        
    # Enforcement 4: Formula assumption
    if not growth_type:
        raise ValueError("REFUSED: --growth-type not specified. Please specify explicitly (e.g., MoM). Never guessing intended formula.")
        
    # Filter dataset strictly to per-ward per-category
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    output_table = []
    
    if growth_type.upper() == 'MOM':
        for i, row in enumerate(filtered):
            period = row['period']
            spend_str = row['actual_spend'].strip() if row.get('actual_spend') else ''
            notes = row.get('notes', '')
            
            if not spend_str:
                growth_str = "Must be flagged - not computed"
                formula_str = "Explicit NULL handling (Equation suspended)"
                out_item = {
                    'Period': period,
                    'Ward': ward,
                    'Category': category,
                    'Actual Spend (₹ lakh)': 'NULL',
                    'MoM Growth': growth_str,
                    'Formula Used': formula_str
                }
            else:
                spend = float(spend_str)
                if i == 0:
                    growth_str = "n/a"
                    formula_str = "n/a (First month of year)"
                else:
                    prev_spend_str = filtered[i-1]['actual_spend'].strip() if filtered[i-1].get('actual_spend') else ''
                    if not prev_spend_str:
                        growth_str = "n/a"
                        formula_str = "n/a (Previous period was NULL)"
                    else:
                        prev_spend = float(prev_spend_str)
                        if prev_spend == 0:
                            growth_str = "infinity"
                            formula_str = f"({spend} - {prev_spend}) / {prev_spend} * 100"
                        else:
                            pct = ((spend - prev_spend) / prev_spend) * 100
                            sign = "+" if pct > 0 else ""
                            notes_str = f" ({notes})" if notes else ""
                            growth_str = f"{sign}{pct:.1f}%{notes_str}"
                            formula_str = f"({spend} - {prev_spend}) / {prev_spend} * 100"
                
                out_item = {
                    'Period': period,
                    'Ward': ward,
                    'Category': category,
                    'Actual Spend (₹ lakh)': spend_str,
                    'MoM Growth': growth_str,
                    'Formula Used': formula_str
                }
            output_table.append(out_item)
            
    else:
        raise ValueError(f"REFUSED: Unrecognized growth type '{growth_type}'. Cannot assume formula.")
        
    return output_table

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Category name")
    parser.add_argument("--growth-type", required=False, help="Growth type e.g., MoM")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    if not args.ward or not args.category:
        print("REFUSED: Missing --ward or --category. Never aggregate across wards or categories.", file=sys.stderr)
        sys.exit(1)
        
    if not args.growth_type:
        print("REFUSED: --growth-type not specified. Never guess the growth formula.", file=sys.stderr)
        sys.exit(1)
    
    try:
        data = load_dataset(args.input)
        result_table = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if result_table:
            with open(args.output, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['Period', 'Ward', 'Category', 'Actual Spend (₹ lakh)', 'MoM Growth', 'Formula Used']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(result_table)
            print(f"Done. Per-ward per-category table written to {args.output}")
        else:
            print("No matching data found for the specified ward/category.")
            
    except ValueError as ve:
        print(ve, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
 