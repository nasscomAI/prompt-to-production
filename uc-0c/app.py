import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.", file=sys.stderr)
        sys.exit(1)
        
    data = []
    null_rows = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames or [])):
            print(f"Error: Missing columns. Expected: {required_cols}", file=sys.stderr)
            sys.exit(1)
            
        for row in reader:
            data.append(row)
            if not row.get('actual_spend') or row['actual_spend'].strip() == '':
                null_rows.append(row)
                
    # Enforcement rule 2: Flag every null row before computing
    if null_rows:
        print(f"Found {len(null_rows)} explicitly null actual_spend rows globally:")
        for r in null_rows:
            reason = r.get('notes', 'No notes given').strip()
            print(f" - {r['period']} | {r['ward']} | {r['category']} -> Reason: {reason}")
    else:
        print("No null actual_spend rows found.")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward, category, and growth_type, returns per-period table with formula shown.
    """
    # Enforcement Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or ward.lower() == "all" or not category or category.lower() == "all":
        print("Refusal: Cannot aggregate across all wards or categories. Refusing computation.", file=sys.stderr)
        sys.exit(1)

    # Filter strictly for single ward and single category
    target_data = [d for d in data if d['ward'].lower() == ward.lower() and d['category'].lower() == category.lower()]
    target_data.sort(key=lambda x: x['period'])

    if not target_data:
        print("No data found for the specified ward and category.", file=sys.stderr)
        return []

    results = []
    for i in range(len(target_data)):
        row = target_data[i]
        period = row['period']
        actual_spend_str = row.get('actual_spend', '').strip()
        notes_str = row.get('notes', '').strip()
        
        out_row = {
            'period': period,
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': actual_spend_str if actual_spend_str else "NULL",
            'computed_growth': '',
            'formula': ''
        }

        # Enforcement rule 2 (apply locally per row for exact output): Flag nulls
        if not actual_spend_str:
            out_row['computed_growth'] = "Flagged: NULL"
            out_row['formula'] = f"Not computed (Reason: {notes_str})"
            results.append(out_row)
            continue

        try:
            curr_val = float(actual_spend_str)
        except ValueError:
            out_row['computed_growth'] = "Error: Invalid number"
            out_row['formula'] = "Not computed"
            results.append(out_row)
            continue

        if growth_type.lower() == 'mom':
            if i > 0:
                prev_row = target_data[i-1]
                prev_spend_str = prev_row.get('actual_spend', '').strip()
                if not prev_spend_str:
                    out_row['computed_growth'] = "n/a (Prev NULL)"
                    out_row['formula'] = "Not computed because prev month is NULL"
                else:
                    try:
                        prev_val = float(prev_spend_str)
                        if prev_val == 0:
                            out_row['computed_growth'] = "n/a (Div by Zero)"
                            out_row['formula'] = f"({curr_val} - 0) / 0"
                        else:
                            pct_change = ((curr_val - prev_val) / prev_val) * 100
                            # format like +33.1% (monsoon spike)
                            sign = '+' if pct_change > 0 else ''
                            note_append = f" ({notes_str})" if notes_str else ""
                            out_row['computed_growth'] = f"{sign}{pct_change:.1f}%{note_append}"
                            # Enforcement rule 3: Show formula used
                            out_row['formula'] = f"(({curr_val} - {prev_val}) / {prev_val}) * 100"
                    except ValueError:
                        out_row['computed_growth'] = "n/a (Prev invalid)"
                        out_row['formula'] = "Not computed"
            else:
                out_row['computed_growth'] = "n/a (First month)"
                out_row['formula'] = "No previous month to compare"
                
        else:
            out_row['computed_growth'] = f"n/a (Unsupported {growth_type})"
            out_row['formula'] = f"{growth_type} computation not implemented"

        results.append(out_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis Agent")
    parser.add_argument("--input", required=True, help="Path to input dataset CSV")
    parser.add_argument("--ward", required=True, help="Target Ward to analyze")
    parser.add_argument("--category", required=True, help="Target Category to analyze")
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV table")
    
    args = parser.parse_args()
    
    # Enforcement rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type not specified. I refuse to guess the target growth metric. Please provide it (e.g., MoM).", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading dataset from {args.input}...")
    dataset = load_dataset(args.input)
    
    print(f"\nComputing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'...")
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No output generated.", file=sys.stderr)
        sys.exit(1)
        
    # Write output
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'computed_growth', 'formula']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nSuccessfully wrote per-ward per-category output to {args.output}")

if __name__ == "__main__":
    main()
