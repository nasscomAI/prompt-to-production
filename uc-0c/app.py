import argparse
import csv
import sys
import os


def load_dataset(file_path):
    """
    Skill 1: Reads the CSV dataset, validates expected columns, counts nulls,
    and explicitly reports which rows have nulls before returning the data.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            fieldnames = reader.fieldnames
    except Exception as e:
        sys.exit(f"Error loading dataset: {e}")

    expected_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not fieldnames or not expected_columns.issubset(set(fieldnames)):
        sys.exit(f"Error: Missing expected columns. Required: {expected_columns}")

    null_rows = []
    print("--- Null 'actual_spend' Report ---")
    for row in data:
        spend = row.get('actual_spend', '').strip()
        if not spend or spend.lower() == 'null':
            null_rows.append(row)
            reason = row.get('notes', 'None')
            print(f"Flagging NULL row: {row['period']} | {row['ward']} | {row['category']} - Reason: {reason}")
            row['actual_spend'] = None
        else:
            try:
                row['actual_spend'] = float(spend)
            except ValueError:
                row['actual_spend'] = None
                
    if null_rows:
        print(f"Total nulls explicitly flagged: {len(null_rows)}\n")
    else:
        print("No null 'actual_spend' values found.\n")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill 2: Computes growth metrics (like MoM) for a specific ward and category, 
    returning a per-period table that includes the growth formula used.
    """
    if not growth_type:
        sys.exit("Refusal: --growth-type not specified. I will not guess the growth metric requested.")

    if not ward or not category or ward.lower() in ['all', 'any'] or category.lower() in ['all', 'any']:
        sys.exit("Refusal: Aggregation across wards or categories is prohibited. Refusing explicitly.")
        
    filtered = [d for d in data if d['ward'] == ward and d['category'] == category]
    
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    if growth_type.lower() == 'mom':
        for i, current in enumerate(filtered):
            out = {
                'Ward': current['ward'],
                'Category': current['category'],
                'Period': current['period'],
                'Actual Spend (₹ lakh)': 'NULL' if current['actual_spend'] is None else f"{current['actual_spend']:.1f}" if isinstance(current['actual_spend'], float) else current['actual_spend'],
                'MoM Growth': '',
                'Formula': ''
            }
            
            if current['actual_spend'] is None:
                out['MoM Growth'] = 'Must be flagged — not computed'
                out['Formula'] = 'N/A'
            elif i == 0:
                out['MoM Growth'] = 'No previous data'
                out['Formula'] = 'N/A'
            else:
                prev = filtered[i-1]
                if prev['actual_spend'] is None:
                    out['MoM Growth'] = 'Previous month is NULL — not computed'
                    out['Formula'] = 'N/A'
                else:
                    curr_val = current['actual_spend']
                    prev_val = prev['actual_spend']
                    if prev_val == 0:
                        out['MoM Growth'] = 'Infinity'
                        out['Formula'] = f"({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}"
                    else:
                        growth_pct = ((curr_val - prev_val) / prev_val) * 100
                        sign = "+" if growth_pct > 0 else "−" if growth_pct < 0 else ""
                        
                        notes = f" ({current['notes']})" if current.get('notes') else ""
                        
                        out['MoM Growth'] = f"{sign}{abs(growth_pct):.1f}%{notes}"
                        out['Formula'] = f"((Current - Previous) / Previous) * 100 = (({curr_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}) * 100"
                        
            results.append(out)
    else:
        sys.exit(f"Refusal: Supported growth_type is 'MoM'. Received '{growth_type}'. Refusing to guess.")
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Validator & Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to save the output CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to limit computation to")
    parser.add_argument("--category", required=True, help="Specific category to limit computation to")
    parser.add_argument("--growth-type", required=False, help="Explicitly specified growth type calculation")
    args = parser.parse_args()

    if not args.growth_type:
        sys.exit("Error: --growth-type must be specified explicitly (e.g., --growth-type MoM). I will never guess.")

    # 1. Load data and explicitly validate/flag nulls
    dataset = load_dataset(args.input)

    # 2. Compute explicit unaggregated growth map
    growth_table = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not growth_table:
        print("Warning: No records found for the specified ward and category.")
    
    # 3. Output as formatted CSV properly named
    try:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            if growth_table:
                fieldnames = list(growth_table[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(growth_table)
        print(f"Success: wrote unaggregated tabular output to {args.output}")
    except Exception as e:
        sys.exit(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
