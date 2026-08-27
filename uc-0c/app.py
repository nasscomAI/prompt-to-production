import argparse
import csv
import sys

def load_dataset(input_path: str, target_ward: str, target_category: str):
    """reads CSV, validates columns, reports null count and which rows before returning"""
    data = []
    null_count = 0
    null_rows = []
    
    # Using utf-8-sig to handle optional BOM ensuring clean header reading
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = row.get('ward', '')
            c = row.get('category', '')
            
            # Simple substring match bypasses encoding/dash errors on Windows
            if target_ward.lower() in w.lower() and target_category.lower() in c.lower():
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend:
                    null_count += 1
                    notes = row.get('notes', 'No reason provided')
                    null_rows.append(f"Period {row['period']}: {notes}")
                
                data.append(row)
                
    if null_count > 0:
        print(f"Warning: Found {null_count} null actual_spend rows for this selection.")
        for nr in null_rows:
            print(f" - {nr}")
            
    data.sort(key=lambda x: x['period'])
    return data

def compute_growth(data: list, growth_type: str):
    """takes ward + category + growth_type, returns per-period table with formula shown"""
    results = []
    prev_spend = None
    
    for row in data:
        actual_spend_str = row.get('actual_spend', '').strip()
        ward = row.get('ward', '')
        category = row.get('category', '')
        period = row.get('period', '')
        
        if not actual_spend_str:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                f'{growth_type} Growth': 'Must be flagged — not computed',
                'Formula': 'NULL input - aborted computation',
                'Notes': row.get('notes', '')
            })
            # Reset prev_spend safely when hitting a null period to ensure chained growth logic isn't skewed.
            prev_spend = None
            continue
            
        current_spend = float(actual_spend_str)
        
        if prev_spend is None:
            growth_str = "n/a"
            formula = "N/A"
        else:
            growth_val = ((current_spend - prev_spend) / prev_spend) * 100
            sign = "+" if growth_val > 0 else ""
            notes = row.get('notes', '')
            note_str = f" ({notes})" if notes else ""
            growth_str = f"{sign}{growth_val:.1f}%{note_str}"
            formula = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
            
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': str(current_spend),
            f'{growth_type} Growth': growth_str,
            'Formula': formula,
            'Notes': row.get('notes', '')
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path for output csv")
    
    args = parser.parse_args()
    
    # Rule 4: Refuse to guess formula
    if not args.growth_type:
        print("ERROR: --growth-type not specified. Refusing to guess formula. Please explicitly pass MoM or YoY.")
        sys.exit(1)
        
    # Rule 1: Refuse aggregation across wards or categories without explicit commands
    if not args.ward or args.ward.lower() == 'any' or not args.category or args.category.lower() == 'any':
        print("ERROR: Cross-category/ward aggregation requires explicit override flags. Refusing request to protect data granularity.")
        sys.exit(1)
        
    # Only process target data to prevent silent aggregation issues
    # Extract just the identifying words to bypass em-dash formatting issues
    ward_filter = args.ward.replace('Ward 1 – ', '').replace('Ward 1 - ', '')
    data = load_dataset(args.input, ward_filter, args.category)
    results = compute_growth(data, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as fout:
        if results:
            writer = csv.DictWriter(fout, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            
    print(f"Done. Processed {len(results)} rows. Results written to {args.output}")

if __name__ == "__main__":
    main()
