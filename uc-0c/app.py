import csv
import sys
import argparse
import os

def load_dataset(input_path: str):
    """
    Reads the CSV budget dataset, validates expected columns, and explicitly 
    reports the total count and exact locations of any null values.
    """
    if not os.path.exists(input_path):
        print(f"Error: dataset '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    expected_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    null_rows = []
    dataset = []
    
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Validate columns
            for col in expected_cols:
                if col not in reader.fieldnames:
                    print(f"Error: Malformed file. Missing expected column: {col}", file=sys.stderr)
                    sys.exit(1)
                    
            for row_idx, row in enumerate(reader, start=2):
                dataset.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append({
                        'row': row_idx,
                        'period': row['period'],
                        'ward': row['ward'],
                        'category': row['category'],
                        'notes': row['notes']
                    })
    except Exception as e:
        print(f"Error reading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Actively report deliberate nulls and prevent silent null handling
    print(f"--- LOAD_DATASET DIAGNOSTICS ---")
    print(f"Total rows successfully loaded: {len(dataset)}")
    print(f"Total explicitly flagged null ('actual_spend' is blank) rows: {len(null_rows)}")
    for null_info in null_rows:
        print(f" - Row {null_info['row']} | {null_info['period']} | {null_info['ward']} | {null_info['category']} => Flagged Reason: {null_info['notes']}")
    print(f"--------------------------------\n")
    
    return dataset

def compute_growth(dataset, ward, category, growth_type):
    """
    Calculates specified growth metric for a strictly defined single ward and single category.
    """
    # Enforce strict scope compliance: no cross-aggregation
    if not ward or ward.lower() == "any":
        print("Error: Never aggregate across wards. Explicit ward must be provided.", file=sys.stderr)
        sys.exit(1)
        
    if not category or category.lower() == "any":
        print("Error: Never aggregate across categories. Explicit category must be provided.", file=sys.stderr)
        sys.exit(1)
        
    if not growth_type:
        print("Error: --growth-type not specified. System must refuse and ask. Never guess the intended formula.", file=sys.stderr)
        sys.exit(1)
        
    if growth_type.lower() != "mom":
        print(f"Error: Unsupported growth type '{growth_type}'. Only MoM verified for this configuration.", file=sys.stderr)
        sys.exit(1)
        
    # Isolate data for specific ward & category
    filtered = []
    for row in dataset:
        if row['ward'] == ward and row['category'] == category:
            filtered.append(row)
            
    filtered.sort(key=lambda x: x['period'])
    
    output_table = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes'].strip()
        
        # Enforce Explicit Null Handling
        if not actual_str:
            output_table.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': "NULL",
                'MoM Growth': "FLAGGED - NOT COMPUTED",
                'Formula': "N/A",
                'Notes': f"Null Reason: {notes}"
            })
            continue
            
        current_spend = float(actual_str)
        
        # Base condition for first period
        if i == 0:
            output_table.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': current_spend,
                'MoM Growth': "N/A",
                'Formula': "N/A",
                'Notes': ""
            })
            continue
            
        prev_row = filtered[i-1]
        prev_actual_str = prev_row['actual_spend'].strip()
        
        if not prev_actual_str:
            # Enforce error cascading: Prev is null so growth cannot be securely computed
            output_table.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': current_spend,
                'MoM Growth': "UNAVAILABLE",
                'Formula': "Cannot compute: Prev period was NULL",
                'Notes': ""
            })
        else:
            prev_spend = float(prev_actual_str)
            if prev_spend == 0:
                output_table.append({
                    'Ward': ward,
                    'Category': category,
                    'Period': period,
                    'Actual Spend': current_spend,
                    'MoM Growth': "INF",
                    'Formula': f"({current_spend} - {prev_spend}) / {prev_spend}",
                    'Notes': "Previous spend was zero"
                })
            else:
                growth_val = (current_spend - prev_spend) / prev_spend
                growth_perc = growth_val * 100
                
                sign = "+" if growth_perc > 0 else ""
                growth_str = f"{sign}{growth_perc:.1f}%"
                
                # Rule 3: Enforce Formula Output Documentation
                formula_str = f"({current_spend} - {prev_spend}) / {prev_spend}"
                
                output_table.append({
                    'Ward': ward,
                    'Category': category,
                    'Period': period,
                    'Actual Spend': current_spend,
                    'MoM Growth': growth_str,
                    'Formula': formula_str,
                    'Notes': ""
                })

    return output_table


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze (Must not be 'Any')")
    parser.add_argument("--category", required=False, help="Specific category to analyze (Must not be 'Any')")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM)")
    
    args = parser.parse_args()
    
    # Pre-computation constraint checks
    if getattr(args, "ward", None) is None or getattr(args, "category", None) is None:
        print("CRITICAL ERROR: Refusing to aggregate broadly. You must specify exact --ward and --category.", file=sys.stderr)
        sys.exit(1)
        
    if getattr(args, "growth_type", None) is None:
        print("CRITICAL ERROR: --growth-type not specified. System must refuse to proceed and explicitly ask. Never guess the intended formula.", file=sys.stderr)
        sys.exit(1)
        
    # Execute Skills Pipeline
    dataset = load_dataset(args.input)
    
    output_table = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend', 'MoM Growth', 'Formula', 'Notes'])
        writer.writeheader()
        writer.writerows(output_table)
        
    print(f"Success. Wrote {len(output_table)} metric rows strictly verified for missing variables to {args.output}")
