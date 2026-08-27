"""
UC-0C app.py — Rule-based implementation.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the CSV, validates columns, and reports null count and exact rows with nulls before returning data.
    """
    data = []
    null_rows = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Handle potential BOM if present
            content = f.read()
            if content.startswith('\ufeff'):
                content = content[1:]
                
            reader = csv.DictReader(content.splitlines())
            
            for i, row in enumerate(reader, start=2): # +1 for header, +1 for 0-index
                data.append(row)
                if not row.get('actual_spend') or row['actual_spend'].strip() == '':
                    null_rows.append({
                        'row_num': i,
                        'period': row.get('period', ''),
                        'ward': row.get('ward', ''),
                        'category': row.get('category', ''),
                        'notes': row.get('notes', 'No reason provided')
                    })
                    
        # Enforcement Rule 2: Report null count and which rows
        if null_rows:
            print(f"WARNING: Found {len(null_rows)} deliberately null 'actual_spend' values.", file=sys.stderr)
            for nr in null_rows:
                print(f"  - Row {nr['row_num']}: {nr['period']} · {nr['ward']} · {nr['category']} (Reason: {nr['notes']})", file=sys.stderr)
                
        return data
        
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes the dataset, filters by ward and category, and computes the requested growth type, 
    returning a per-period table with the formula shown.
    """
    # Enforcement Rule 4: Refuse if growth_type missing or invalid
    if not growth_type:
        print("ERROR: --growth-type must be specified. I will not guess between MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    if growth_type.upper() != "MOM":
        print(f"ERROR: Only MoM growth is supported in this implementation, received: {growth_type}", file=sys.stderr)
        sys.exit(1)

    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or not category:
        print("ERROR: I refuse to aggregate across all wards or categories. You must specify a specific --ward and --category.", file=sys.stderr)
        sys.exit(1)

    if ward.lower() == "any" or category.lower() == "any":
        print("ERROR: I refuse to aggregate across all wards or categories. Please provide a specific ward and category.", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"WARNING: No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        return []

    # Sort chronologically by period
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    
    for i in range(len(filtered_data)):
        current = filtered_data[i]
        period = current['period']
        current_spend_str = current.get('actual_spend', '').strip()
        
        result_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (\u20b9 lakh)': current_spend_str if current_spend_str else "NULL",
            'MoM Growth': '',
            'Formula': ''
        }
        
        if i == 0:
            result_row['MoM Growth'] = "n/a"
            result_row['Formula'] = "No previous month"
            results.append(result_row)
            continue
            
        previous = filtered_data[i-1]
        prev_spend_str = previous.get('actual_spend', '').strip()
        
        # Enforcement Rule 2: Flag every null row before computing
        if not current_spend_str:
            reason = current.get('notes', 'Missing data')
            result_row['MoM Growth'] = f"FLAGGED NULL: {reason}"
            result_row['Formula'] = "Cannot compute with null current month"
        elif not prev_spend_str:
            reason = previous.get('notes', 'Missing data')
            result_row['MoM Growth'] = f"FLAGGED NULL in previous month: {reason}"
            result_row['Formula'] = "Cannot compute with null previous month"
        else:
            try:
                curr_val = float(current_spend_str)
                prev_val = float(prev_spend_str)
                
                if prev_val == 0:
                    result_row['MoM Growth'] = "Infinite"
                    result_row['Formula'] = f"({curr_val} - {prev_val}) / {prev_val}"
                else:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    sign = "+" if growth > 0 else ""
                    result_row['MoM Growth'] = f"{sign}{growth:.1f}%"
                    
                    # Enforcement Rule 3: Show formula
                    result_row['Formula'] = f"({curr_val} - {prev_val}) / {prev_val} * 100"
            except ValueError:
                result_row['MoM Growth'] = "ERROR: Invalid number format"
                result_row['Formula'] = "N/A"
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", help="Target ward to analyze")
    parser.add_argument("--category", help="Target category to analyze")
    parser.add_argument("--growth-type", help="Type of growth to calculate (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output summary CSV file")
    args = parser.parse_args()

    # Apply skills
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        sys.exit(1)
        
    # Write to output CSV
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (\u20b9 lakh)', 'MoM Growth', 'Formula']
    
    try:
        with open(args.output, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth calculation completed successfully. Output saved to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
