import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the budget CSV file, validates required columns, and reports missing data before returning.
    """
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_count = 0
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames if reader.fieldnames else [])
            
            if not required_columns.issubset(headers):
                print(f"Error: Missing required columns.\nExpected at least: {required_columns}\nFound: {headers}", file=sys.stderr)
                sys.exit(1)
                
            for i, row in enumerate(reader, start=2): # 1-indexed plus header
                actual_spend = row.get('actual_spend', '').strip()
                if not actual_spend or actual_spend.lower() == 'null':
                    null_count += 1
                    null_rows.append(f"Row {i}: Period {row.get('period')} · {row.get('ward')} · {row.get('category')} - Note: {row.get('notes')}")
                data.append(row)
                
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Dataset loaded successfully. Total rows: {len(data)}")
    if null_count > 0:
        print(f"Found {null_count} rows with null actual_spend:")
        for r in null_rows:
            print(f"  - {r}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes the growth table for a single ward and category over time, including the formula used.
    """
    # Defensive checks
    if not growth_type:
        print("Error: --growth-type not specified. Cannot guess growth type. Please provide --growth-type (e.g., MoM).", file=sys.stderr)
        sys.exit(1)
        
    if not ward or not category:
        print("Error: Aggregation across multiple wards or categories is strictly prohibited. Please specify both --ward and --category.", file=sys.stderr)
        sys.exit(1)
        
    # Filter data for specific ward and category
    filtered_data = [row for row in data if row.get('ward', '').strip() == ward.strip() and row.get('category', '').strip() == category.strip()]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'.")
        return [], []
        
    # Ensure periods are sorted chronologically
    filtered_data.sort(key=lambda x: x.get('period', ''))
    
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row.get('period')
        actual_spend_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '').strip()
        
        is_null = not actual_spend_str or actual_spend_str.lower() == 'null'
        
        growth_result = ""
        formula = ""
        actual_spend_val = None
        
        if is_null:
            growth_result = f"Must be flagged — not computed (Reason: {notes})"
            formula = "n/a"
        else:
            try:
                actual_spend_val = float(actual_spend_str)
            except ValueError:
                actual_spend_val = 0.0
                
            if growth_type.lower() == "mom":
                if i == 0:
                    growth_result = "n/a"
                    formula = "No prior period"
                else:
                    prev_row = filtered_data[i-1]
                    prev_spend_str = prev_row.get('actual_spend', '').strip()
                    prev_is_null = not prev_spend_str or prev_spend_str.lower() == 'null'
                    
                    if prev_is_null:
                        growth_result = "n/a (Previous period NULL)"
                        formula = "Cannot divide by NULL"
                    else:
                        try:
                            prev_val = float(prev_spend_str)
                            if prev_val == 0:
                                growth_result = "n/a (Divide by zero)"
                                formula = f"({actual_spend_val} - 0) / 0"
                            else:
                                growth = ((actual_spend_val - prev_val) / prev_val) * 100
                                sign = "+" if growth > 0 else "−" if growth < 0 else "" # using minus sign as requested by README
                                abs_growth = abs(growth)
                                suffix = f" ({notes})" if notes else ""
                                growth_result = f"{sign}{abs_growth:.1f}%{suffix}"
                                formula = f"({actual_spend_val} - {prev_val}) / {prev_val} * 100"
                        except ValueError:
                            growth_result = "n/a (Invalid previous value)"
                            formula = "Error parsing previous value"
            elif growth_type.lower() == "yoy":
                # Assuming period format is YYYY-MM
                try:
                    curr_year, curr_month = period.split('-')
                    prev_period = f"{int(curr_year)-1}-{curr_month}"
                    
                    prev_row = next((r for r in filtered_data if r.get('period') == prev_period), None)
                    
                    if not prev_row:
                        growth_result = "n/a"
                        formula = "No prior year period"
                    else:
                        prev_spend_str = prev_row.get('actual_spend', '').strip()
                        prev_is_null = not prev_spend_str or prev_spend_str.lower() == 'null'
                        
                        if prev_is_null:
                            growth_result = "n/a (Previous year NULL)"
                            formula = "Cannot divide by NULL"
                        else:
                            try:
                                prev_val = float(prev_spend_str)
                                if prev_val == 0:
                                    growth_result = "n/a (Divide by zero)"
                                    formula = f"({actual_spend_val} - 0) / 0"
                                else:
                                    growth = ((actual_spend_val - prev_val) / prev_val) * 100
                                    sign = "+" if growth > 0 else "−" if growth < 0 else ""
                                    abs_growth = abs(growth)
                                    suffix = f" ({notes})" if notes else ""
                                    growth_result = f"{sign}{abs_growth:.1f}%{suffix}"
                                    formula = f"({actual_spend_val} - {prev_val}) / {prev_val} * 100"
                            except ValueError:
                                growth_result = "n/a (Invalid previous value)"
                                formula = "Error parsing previous value"
                except ValueError:
                    growth_result = "n/a"
                    formula = "Invalid period format for YoY"
            else:
                print(f"Error: Unknown --growth-type '{growth_type}' provided.", file=sys.stderr)
                sys.exit(1)
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': 'NULL' if is_null else actual_spend_str,
            f'{growth_type} Growth': growth_result,
            'Formula': formula
        })
        
    # Return fieldnames based on actual results and the growth_type
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{growth_type} Growth', 'Formula']
    return results, fieldnames


def main():
    parser = argparse.ArgumentParser(description="Data Growth Analysis Agent Output")
    
    # We use arguments without required=True first to enforce manual checks based on rules
    parser.add_argument("--input", help="Path to input CSV dataset.")
    parser.add_argument("--ward", help="Target ward to calculate growth for.")
    parser.add_argument("--category", help="Target category to calculate growth for.")
    parser.add_argument("--growth-type", dest="growth_type", help="Type of growth calculation (e.g., MoM, YoY).")
    parser.add_argument("--output", help="Path to save output CSV.")
    
    args = parser.parse_args()
    
    # Validation
    if not args.input:
        print("Error: --input is required.", file=sys.stderr)
        sys.exit(1)
    if not args.output:
        print("Error: --output is required.", file=sys.stderr)
        sys.exit(1)
    
    # --- ENFORCEMENT RULES START ---
    
    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type not specified. I cannot assume a growth type. Please provide a --growth-type (e.g., MoM, YoY).", file=sys.stderr)
        sys.exit(1)
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward or not args.category:
        print("Error: Refusing to aggregate across wards or categories. You must specify both --ward and --category precisely.", file=sys.stderr)
        sys.exit(1)
        
    # --- ENFORCEMENT RULES END ---
    
    # Skill 1: load_dataset (includes checking and reporting on NULL values)
    print("Loading dataset...", file=sys.stderr)
    data = load_dataset(args.input)
    
    # Skill 2: compute_growth (calculates metric per period separately, appending formula)
    print(f"Computing {args.growth_type} growth for '{args.ward}' - '{args.category}'...", file=sys.stderr)
    results, fieldnames = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # Output file saving
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if results:
                writer.writerows(results)
        print(f"Growth calculation table successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
