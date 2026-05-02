import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not reader.fieldnames:
                raise ValueError("CSV file is empty or missing headers.")
            
            missing_cols = [col for col in required_columns if col not in reader.fieldnames]
            if missing_cols:
                raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
            
            for row in reader:
                data.append(row)
                
                # Check for null actual_spend
                val = row.get("actual_spend", "").strip()
                if not val or val.lower() == "null":
                    null_rows.append(row)
                    
    except FileNotFoundError:
        print(f"Error: Could not find file {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Dataset loaded. Found {len(null_rows)} rows with NULL actual_spend:")
    for row in null_rows:
        print(f"  - {row['period']} · {row['ward']} · {row['category']} -> Reason: {row.get('notes', 'None')}")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses if aggregated across wards/categories.
    """
    if not ward or not category:
        print("Error: Must specify both --ward and --category. Aggregation is not allowed.", file=sys.stderr)
        sys.exit(1)
        
    if ward.lower() == "all" or category.lower() == "all":
        print("Error: Aggregating across all wards or categories is explicitly forbidden by enforcement rules.", file=sys.stderr)
        sys.exit(1)
        
    if not growth_type:
        print("Error: --growth-type must be specified.", file=sys.stderr)
        sys.exit(1)
        
    # Filter data
    filtered_data = [
        row for row in data 
        if row['ward'].lower() == ward.lower() and row['category'].lower() == category.lower()
    ]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}', Category: '{category}'")
        return []
        
    # Sort chronologically by period (YYYY-MM)
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered_data):
        current_spend_str = row.get('actual_spend', '').strip()
        is_current_null = not current_spend_str or current_spend_str.lower() == 'null'
        
        output_row = {
            'ward': row['ward'],
            'category': row['category'],
            'period': row['period'],
            'budgeted_amount': row.get('budgeted_amount', ''),
            'actual_spend': row.get('actual_spend', ''),
            'notes': row.get('notes', ''),
            f'{growth_type}_growth': '',
            'formula': ''
        }
        
        if is_current_null:
            output_row[f'{growth_type}_growth'] = 'FLAGGED: NULL'
            output_row['formula'] = 'Cannot compute: Current period is NULL'
            results.append(output_row)
            continue
            
        current_spend = float(current_spend_str)
        
        # Find comparison period
        prev_row = None
        if growth_type.lower() == 'mom':
            if i > 0:
                prev_row = filtered_data[i-1]
        elif growth_type.lower() == 'yoy':
            # Look for same month, previous year
            curr_year, curr_month = row['period'].split('-')
            target_period = f"{int(curr_year)-1}-{curr_month}"
            
            for p_row in filtered_data:
                if p_row['period'] == target_period:
                    prev_row = p_row
                    break
        else:
            print(f"Error: Unknown growth type '{growth_type}'. Use MoM or YoY.", file=sys.stderr)
            sys.exit(1)
            
        if not prev_row:
            output_row[f'{growth_type}_growth'] = 'N/A'
            output_row['formula'] = 'No prior period data available'
            results.append(output_row)
            continue
            
        prev_spend_str = prev_row.get('actual_spend', '').strip()
        is_prev_null = not prev_spend_str or prev_spend_str.lower() == 'null'
        
        if is_prev_null:
            output_row[f'{growth_type}_growth'] = 'FLAGGED: PREV NULL'
            output_row['formula'] = 'Cannot compute: Previous period is NULL'
            results.append(output_row)
            continue
            
        prev_spend = float(prev_spend_str)
        
        if prev_spend == 0:
            output_row[f'{growth_type}_growth'] = 'N/A'
            output_row['formula'] = f'({current_spend} - 0) / 0'
        else:
            pct = ((current_spend - prev_spend) / prev_spend) * 100
            sign = "+" if pct > 0 else ""
            output_row[f'{growth_type}_growth'] = f'{sign}{pct:.1f}%'
            output_row['formula'] = f'({current_spend} - {prev_spend}) / {prev_spend}'
            
        results.append(output_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Data Analyst: Calculates period-over-period growth metrics.")
    parser.add_argument('--input', required=True, help="Path to input CSV file")
    parser.add_argument('--ward', required=True, help="Specific ward to analyze (required)")
    parser.add_argument('--category', required=True, help="Specific category to analyze (required)")
    parser.add_argument('--growth-type', required=True, help="Growth type to compute (e.g., MoM, YoY)")
    parser.add_argument('--output', required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    # 1. Load Dataset
    data = load_dataset(args.input)
    
    # 2. Compute Growth
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No results to write. Exiting.")
        sys.exit(0)
        
    # 3. Write Output
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully wrote output to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
