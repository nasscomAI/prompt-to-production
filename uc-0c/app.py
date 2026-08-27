"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

# ==========================================
# SKILL 1: load_dataset
# ==========================================
def load_dataset(file_path):
    """
    Reads the budget CSV file, validates columns, and explicitly identifies 
    rows with null actual_spend values to prevent silent null handling.
    """
    if not os.path.exists(file_path):
        print(f"Error [load_dataset]: File '{file_path}' cannot be read.", file=sys.stderr)
        sys.exit(1)

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    dataset = []
    null_report = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            if not all(col in reader.fieldnames for col in required_columns):
                print(f"Error [load_dataset]: Missing required columns. Expected {required_columns}", file=sys.stderr)
                sys.exit(1)

            for row_idx, row in enumerate(reader, start=2): # Start at 2 for header
                dataset.append(row)
                
                # Check for null or blank actual_spend
                spend_val = row['actual_spend'].strip()
                if not spend_val or spend_val.lower() in ['null', 'nan', 'none']:
                    null_report.append({
                        'row': row_idx,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row['notes']
                    })
    except Exception as e:
        print(f"Error [load_dataset]: Failed to process file. {e}", file=sys.stderr)
        sys.exit(1)

    # Print explicit null report to stdout as required by enforcement
    if null_report:
        print(f"--- NULL VALUE REPORT ({len(null_report)} rows detected) ---")
        for null_row in null_report:
            print(f"FLAG: Null actual_spend found in {null_row['period']} for {null_row['ward']} / {null_row['category']}. Reason: {null_row['notes']}")
        print("--------------------------------------------------\n")

    return dataset

# ==========================================
# SKILL 2: compute_growth
# ==========================================
def compute_growth(dataset, ward, category, growth_type):
    """
    Calculates growth metric for a strictly defined ward and category over time,
    returning a per-period table with explicit mathematical formulas attached.
    """
    # Enforcement 4: Formula assumption prevention
    if not growth_type:
        print("Error [compute_growth]: REFUSED. --growth-type was not specified. I cannot assume whether you want MoM, YoY, etc. Please specify explicitly.", file=sys.stderr)
        sys.exit(1)

    if growth_type.upper() != "MOM":
         print(f"Error [compute_growth]: Only MoM is implemented in this scope, requested '{growth_type}'.", file=sys.stderr)
         sys.exit(1)

    # Enforcement 1: Aggregation prevention
    if not ward or str(ward).lower() in ['any', 'all'] or not category or str(category).lower() in ['any', 'all']:
        print("Error [compute_growth]: REFUSED. Never aggregate across wards or categories unless explicitly instructed. Please specify an exact ward and category.", file=sys.stderr)
        sys.exit(1)

    # Filter data strictly to the specified ward and category
    filtered_data = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'.")
        return []

    # Sort sequentially by period (YYYY-MM)
    filtered_data = sorted(filtered_data, key=lambda x: x['period'])

    results = []
    previous_spend = None

    for i, row in enumerate(filtered_data):
        current_period = row['period']
        current_spend_raw = row['actual_spend'].strip()
        notes = row['notes']
        
        # Enforcement 2: Silent null handling prevention
        is_null = not current_spend_raw or current_spend_raw.lower() in ['null', 'nan', 'none']
        
        if is_null:
            results.append({
                'period': current_period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth_result': 'NOT COMPUTED',
                'formula': 'N/A',
                'flag': f"NEEDS_REVIEW: Missing data. Reason: {notes}"
            })
            previous_spend = None # Reset previous spend since chain is broken
            continue

        current_spend = float(current_spend_raw)

        # Calculate MoM
        if previous_spend is None:
            results.append({
                'period': current_period,
                'ward': ward,
                'category': category,
                'actual_spend': current_spend,
                'growth_result': 'N/A',
                'formula': 'No previous valid period to calculate MoM',
                'flag': ''
            })
        else:
            growth_val = ((current_spend - previous_spend) / previous_spend) * 100
            
            # Enforcement 3: Show formula used in every output row
            formula_str = f"(({current_spend} - {previous_spend}) / {previous_spend}) * 100"
            
            results.append({
                'period': current_period,
                'ward': ward,
                'category': category,
                'actual_spend': current_spend,
                'growth_result': f"{growth_val:+.1f}%",
                'formula': formula_str,
                'flag': ''
            })
            
        previous_spend = current_spend

    return results

# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="UC-0C: Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to input budget CSV")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific category (e.g. 'Roads & Pothole Repair')")
    # Not using required=True here to allow testing of the "refuse and ask" enforcement rule
    parser.add_argument("--growth-type", help="Type of growth to calculate (e.g., MoM)") 
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()

    print(f"Loading dataset: {args.input}...")
    dataset = load_dataset(args.input)
    
    print(f"Computing {args.growth_type} growth for '{args.ward}' - '{args.category}'...")
    growth_table = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not growth_table:
        print("No output generated due to empty dataset for given parameters.")
        sys.exit(0)

    # Output Management
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    
    output_columns = ['period', 'ward', 'category', 'actual_spend', 'growth_result', 'formula', 'flag']
    
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_columns)
            writer.writeheader()
            writer.writerows(growth_table)
        print(f"Success! Output verifiable per-period table written to: {args.output}")
    except Exception as e:
        print(f"Error writing to output file. {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()