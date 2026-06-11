"""
UC-0C — Number That Looks Right
Implementation based on RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    data = []
    null_rows = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if not required_cols.issubset(set(reader.fieldnames)):
                print(f"Error: Missing required columns. Found: {reader.fieldnames}")
                sys.exit(1)
                
            for i, row in enumerate(reader):
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend or actual_spend.lower() == 'null':
                    null_rows.append((row['period'], row['ward'], row['category'], row.get('notes', 'No notes provided')))
                data.append(row)
                
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"--- Dataset Validation: Found {len(null_rows)} rows with NULL actual_spend ---")
        for r in null_rows:
            print(f"  Flagged NULL: {r[0]} | {r[1]} | {r[2]} -> Reason: {r[3]}")
        print("-------------------------------------------------------------------------")
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes dataset, ward, category, growth_type, returns per-period table with formula shown."""
    if not growth_type:
        print("Refusal: --growth-type not specified. Please provide 'MoM' or 'YoY'. I will not guess the formula.")
        sys.exit(1)
        
    if not ward or not category or ward.lower() == 'all' or category.lower() == 'all':
        print("Refusal: Cannot aggregate across wards or categories. Please specify an exact ward and category.")
        sys.exit(1)

    # Filter and sort data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        current_row = filtered[i]
        period = current_row['period']
        actual_str = current_row.get('actual_spend', '').strip()
        notes = current_row.get('notes', '')
        
        result_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': actual_str if actual_str else 'NULL',
            'Growth': 'N/A',
            'Formula': f"{growth_type} = (Current - Previous) / Previous * 100",
            'Notes': notes
        }
        
        if not actual_str or actual_str.lower() == 'null':
            result_row['Growth'] = 'NULL (Flagged: Cannot compute due to missing data)'
            results.append(result_row)
            continue
            
        current_val = float(actual_str)
        
        if growth_type.upper() == 'MOM':
            # Need previous month. Since data is monthly and sorted, we can just use i-1 if it exists
            # More robust: check if previous period is actually 1 month prior, but we'll assume sequential sorted here
            if i == 0:
                result_row['Growth'] = 'N/A (First month)'
            else:
                prev_str = filtered[i-1].get('actual_spend', '').strip()
                if not prev_str or prev_str.lower() == 'null':
                    result_row['Growth'] = 'N/A (Previous month is NULL)'
                else:
                    prev_val = float(prev_str)
                    if prev_val == 0:
                        result_row['Growth'] = 'N/A (Div by zero)'
                    else:
                        growth = (current_val - prev_val) / prev_val * 100
                        # Formatting to 1 decimal place with + sign if positive
                        result_row['Growth'] = f"{'+' if growth > 0 else ''}{growth:.1f}%"
        elif growth_type.upper() == 'YOY':
            # For YoY, we'd look 12 indices back if sequential, or parse date. 
            # Given the problem scope, we will implement YoY checking by period parsing.
            curr_year, curr_month = map(int, period.split('-'))
            prev_period = f"{curr_year - 1}-{curr_month:02d}"
            
            # Find the row for prev_period
            prev_row = next((r for r in filtered if r['period'] == prev_period), None)
            if not prev_row:
                result_row['Growth'] = 'N/A (No previous year data)'
            else:
                prev_str = prev_row.get('actual_spend', '').strip()
                if not prev_str or prev_str.lower() == 'null':
                    result_row['Growth'] = 'N/A (Previous year is NULL)'
                else:
                    prev_val = float(prev_str)
                    if prev_val == 0:
                        result_row['Growth'] = 'N/A (Div by zero)'
                    else:
                        growth = (current_val - prev_val) / prev_val * 100
                        result_row['Growth'] = f"{'+' if growth > 0 else ''}{growth:.1f}%"
        else:
            print(f"Refusal: Unknown growth_type '{growth_type}'. Only 'MoM' and 'YoY' supported.")
            sys.exit(1)

        results.append(result_row)
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth to compute (e.g. MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Please provide 'MoM' or 'YoY'. I will not guess the formula.")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("Refusal: Cannot aggregate across wards or categories. Please specify an exact --ward and --category.")
        sys.exit(1)

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            if not results:
                print("No data matched the given ward and category.")
                sys.exit(0)
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully wrote {len(results)} rows to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
