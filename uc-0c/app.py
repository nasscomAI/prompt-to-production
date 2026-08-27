import argparse
import csv
import sys
import os
from datetime import datetime

def load_dataset(file_path):
    """
    Reads the budget CSV file, validates columns, and reports nulls.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
            for col in required_columns:
                if col not in reader.fieldnames:
                    print(f"Error: Missing required column '{col}'")
                    sys.exit(1)
            
            for row in reader:
                try:
                    row['budgeted_amount'] = float(row['budgeted_amount'])
                except (ValueError, TypeError):
                    row['budgeted_amount'] = 0.0
                
                try:
                    if row['actual_spend'] and row['actual_spend'].strip():
                        row['actual_spend'] = float(row['actual_spend'])
                    else:
                        row['actual_spend'] = None
                except (ValueError, TypeError):
                    row['actual_spend'] = None
                
                data.append(row)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    null_count = sum(1 for row in data if row['actual_spend'] is None)
    if null_count > 0:
        print(f"Found {null_count} null rows in 'actual_spend'.")
    
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates growth for a specific ward and category.
    """
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return None

    try:
        filtered.sort(key=lambda x: datetime.strptime(x['period'], '%Y-%m'))
    except Exception as e:
        print(f"Error sorting periods: {e}")
        sys.exit(1)
    
    results = []
    
    for i, current_row in enumerate(filtered):
        period_str = current_row['period']
        actual_spend = current_row['actual_spend']
        notes = current_row['notes']
        
        row_res = {
            'Ward': ward,
            'Category': category,
            'Period': period_str,
            'Actual Spend (Rupees lakh)': actual_spend if actual_spend is not None else 'NULL',
            'MoM Growth': 'n/a',
            'Formula': 'n/a'
        }
        
        if actual_spend is None:
            row_res['MoM Growth'] = f"FLAGGED: {notes}"
            row_res['Formula'] = "N/A (Null Value)"
        elif i > 0:
            prev_row = filtered[i-1]
            prev_spend = prev_row['actual_spend']
            
            if prev_spend is not None and prev_spend != 0:
                growth = ((actual_spend - prev_spend) / prev_spend) * 100
                row_res['MoM Growth'] = f"{growth:+.1f}%"
                row_res['Formula'] = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
            else:
                row_res['MoM Growth'] = "n/a (Prev NULL or 0)"
                row_res['Formula'] = "N/A"
        
        results.append(row_res)
        
    return results

def main():
    # Force UTF-8 for stdout if possible, or just use safer characters
    if sys.stdout.encoding != 'utf-8':
        pass # We've changed the symbol to 'Rupees' to avoid charmap errors
        
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", help="Type of growth (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Error: --growth-type is required. Please specify (e.g., MoM).")
        sys.exit(1)
        
    if args.growth_type != "MoM":
        print(f"Error: Growth type '{args.growth_type}' is not supported yet. Only 'MoM' is implemented.")
        sys.exit(1)

    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully generated growth report: {args.output}")
            
            print("\nPreview of output:")
            header = list(results[0].keys())
            print(" | ".join(header))
            print("-" * 100)
            for row in results:
                print(" | ".join(str(row[k]) for k in header))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
