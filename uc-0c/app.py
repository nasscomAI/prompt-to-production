import argparse
import csv
import sys
import os

def load_dataset(filepath: str):
    """
    Reads the budget CSV file, validates expected columns, and reports the null count 
    and specific rows with missing values before returning the loaded dataset.
    """
    rows = []
    null_report = []
    expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not expected_cols.issubset(set(reader.fieldnames or [])):
                print(f"Error: Dataset missing required columns. Expected: {expected_cols}")
                sys.exit(1)
                
            for row in reader:
                # Flag nulls
                actual = row.get('actual_spend', '').strip()
                if not actual:
                    null_report.append(row)
                rows.append(row)
                
        print(f"Dataset loaded successfully. Total rows: {len(rows)}")
        if null_report:
            print(f"\n--- [AGENT WARNING] Flagged {len(null_report)} row(s) with missing 'actual_spend' ---")
            for r in null_report:
                print(f" -> Period: {r['period']} | Ward: {r['ward']} | Category: {r['category']} | Reason: {r.get('notes', 'No note')}")
            print("--------------------------------------------------------------------------------\n")
            
        return rows
        
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)

def compute_growth(dataset, target_ward, target_category, growth_type):
    """
    Calculates period-over-period growth for a specific ward and category.
    """
    # Enforcement 1 & 4: Refusal logic
    if not target_ward or not target_category:
        print("AGENT REFUSAL: Never aggregate across wards or categories unless explicitly instructed. Both --ward and --category must be specified.")
        sys.exit(1)
        
    if not growth_type:
        print("AGENT REFUSAL: --growth-type not specified. I cannot guess the formula (e.g., choose MoM or YoY for you).")
        sys.exit(1)
        
    # Filter dataset
    filtered = [r for r in dataset if r['ward'] == target_ward and r['category'] == target_category]
    if not filtered:
        print("Warning: No matching data found for the specified ward and category.")
        return []
        
    # Sort chronologically
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered)):
        current_row = filtered[i]
        period = current_row['period']
        current_spend_str = current_row.get('actual_spend', '').strip()
        notes_str = current_row.get('notes', '').strip()
        
        # Format the note append text if any notes are present.
        note_append = f" ({notes_str})" if notes_str else ""
        
        # Prepare output dict
        out_row = {
            'Ward': target_ward,
            'Category': target_category,
            'Period': period,
            'Actual Spend (₹ lakh)': "NULL" if not current_spend_str else current_spend_str,
            f'{growth_type} Growth': '',
            'Formula Used': ''
        }
        
        if not current_spend_str:
            out_row[f'{growth_type} Growth'] = 'Not Computed (NULL)'
            out_row['Formula Used'] = 'n/a (Missing current spend)'
            results.append(out_row)
            continue
            
        try:
            current_spend = float(current_spend_str)
        except ValueError:
            out_row[f'{growth_type} Growth'] = 'ERROR: Invalid format'
            out_row['Formula Used'] = 'n/a'
            results.append(out_row)
            continue
            
        # Determine previous period index based on growth type
        if growth_type.upper() == 'MOM':
            prev_index = i - 1
        elif growth_type.upper() == 'YOY':
            prev_index = i - 12
        else:
            print(f"AGENT REFUSAL: Unrecognized/Unsupported growth type '{growth_type}'.")
            sys.exit(1)
            
        if prev_index < 0:
            out_row[f'{growth_type} Growth'] = 'n/a (No prior data)'
            out_row['Formula Used'] = 'n/a'
            results.append(out_row)
            continue
            
        prev_row = filtered[prev_index]
        prev_spend_str = prev_row.get('actual_spend', '').strip()
        
        if not prev_spend_str:
            out_row[f'{growth_type} Growth'] = 'Not Computed (NULL previous)'
            out_row['Formula Used'] = 'n/a (Missing previous spend)'
            results.append(out_row)
            continue
            
        try:
            prev_spend = float(prev_spend_str)
        except ValueError:
            out_row[f'{growth_type} Growth'] = 'ERROR: Invalid prior format'
            out_row['Formula Used'] = 'n/a'
            results.append(out_row)
            continue
            
        # USER RULE: Guard against zero division
        if prev_spend == 0:
            print(f"AGENT ERROR: Division by 0 attempted at Period {period}. Previous actual_spend is 0.")
            out_row[f'{growth_type} Growth'] = 'ERROR: Div by 0'
            out_row['Formula Used'] = f'({current_spend} - 0) / 0'
            results.append(out_row)
            continue
            
        growth = ((current_spend - prev_spend) / prev_spend) * 100
        
        # Format output
        sign = "+" if growth > 0 else "-" if growth < 0 else ""
        
        # e.g., +33.1% (monsoon spike)
        out_row[f'{growth_type} Growth'] = f"{sign}{abs(growth):.1f}%{note_append}"
        out_row['Formula Used'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
        
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", help="Filepath to the input CSV", default=None)
    parser.add_argument("--ward", help="Specific Ward to analyze (e.g., 'Ward 1 – Kasba')", default=None)
    parser.add_argument("--category", help="Specific Category to analyze", default=None)
    parser.add_argument("--growth-type", help="Growth metric to compute (e.g., MoM)", default=None)
    parser.add_argument("--output", help="Filepath to the output CSV", default=None)
    
    args = parser.parse_args()
    
    # Fallback to test case if no arguments provided
    if not args.input and not args.output:
        print("No specific arguments provided. Assuming default test execution...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        args.input = os.path.join(base_dir, "..", "data", "budget", "ward_budget.csv")
        args.ward = "Ward 1 – Kasba"
        args.category = "Roads & Pothole Repair"
        args.growth_type = "MoM"
        args.output = os.path.join(base_dir, "growth_output.csv")
        
    elif not args.input or not args.output:
        print("Error: Both --input and --output are required if overriding defaults.")
        sys.exit(1)
    
    dataset = load_dataset(args.input)
    
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        # Create directory for output if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"Results successfully computed and written to '{args.output}'.")

if __name__ == "__main__":
    main()
