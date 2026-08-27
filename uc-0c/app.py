import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and logs which rows have nulls.
    """
    expected_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_rows = []
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                raise ValueError("CSV is empty or missing headers.")
            
            # Validate expected columns are present
            missing_cols = [col for col in expected_columns if col not in headers]
            if missing_cols:
                raise ValueError(f"Missing expected columns: {missing_cols}")
            
            for row_num, row in enumerate(reader, start=2): # Start at 2 since row 1 is headers
                data.append(row)
                actual_spend = row.get("actual_spend", "").strip()
                if not actual_spend or actual_spend.lower() == "null":
                    null_rows.append((row_num, row.get("period", ""), row.get("ward", ""), row.get("category", ""), row.get("notes", "")))
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset file '{filepath}' not found.")
        
    print(f"Dataset loaded. Processing {len(data)} rows.")
    
    # Enforcement: Flag every null row before computing AND report null reason from notes
    if null_rows:
        print(f"\n[ENFORCEMENT FLAG] Found {len(null_rows)} explicitly null 'actual_spend' values. Before proceeding, here are the reasons:")
        for r in null_rows:
            print(f"  -> Row {r[0]} | Period: {r[1]} | Ward: {r[2]} | Category: {r[3]} | Reason: {r[4]}")
        print()
    else:
        print("No null 'actual_spend' values found.")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward, category, and growth_type, returns per-period table with formula shown.
    Refuses vague aggregation across wards or categories.
    """
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed
    if not ward or ward.lower() in ("any", "all", "none"):
        raise ValueError("REFUSAL: Cannot aggregate across wards. You must explicitly specify a single ward.")
    
    if not category or category.lower() in ("any", "all", "none"):
        raise ValueError("REFUSAL: Cannot aggregate across categories. You must explicitly specify a single category.")
        
    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unsupported growth type '{growth_type}'. This demonstration exclusively handles MoM.")
        
    # Filter for the specific ward and category
    filtered_data = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    
    # Optional: Sort sequentially by period (assuming YYYY-MM)
    filtered_data = sorted(filtered_data, key=lambda x: x.get('period', ''))
    
    results = []
    
    for i, row in enumerate(filtered_data):
        period = row.get('period')
        actual_spend_str = row.get('actual_spend', '').strip()
        budgeted_amount = row.get('budgeted_amount', '')
        notes = row.get('notes', '')
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': budgeted_amount,
            'actual_spend': actual_spend_str,
            'notes': notes,
            'growth': 'n/a',
            'formula': 'n/a'
        }
        
        if not actual_spend_str or actual_spend_str.lower() == "null":
            result_row['growth'] = 'NULL (Flagged)'
            result_row['formula'] = 'Not computed due to missing actual_spend'
        else:
            try:
                current_spend = float(actual_spend_str)
                if i == 0:
                    result_row['growth'] = 'n/a'
                    result_row['formula'] = 'No previous period'
                else:
                    prev_spend_str = filtered_data[i-1].get('actual_spend', '').strip()
                    if not prev_spend_str or prev_spend_str.lower() == "null":
                        result_row['growth'] = 'n/a'
                        result_row['formula'] = 'Previous period is NULL'
                    else:
                        prev_spend = float(prev_spend_str)
                        if prev_spend == 0:
                            result_row['growth'] = 'n/a (Div by 0)'
                            result_row['formula'] = f'({current_spend} - {prev_spend}) / {prev_spend}'
                        else:
                            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
                            sign = "+" if growth_pct > 0 else ""
                            # We append the formula inline
                            result_row['growth'] = f"{sign}{growth_pct:.1f}%"
                            # Enforcement: Show formula used in every output row alongside the result
                            result_row['formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            except ValueError:
                result_row['growth'] = 'ERROR'
                result_row['formula'] = 'Invalid generic numerical value'
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate verifiable strict growth over specific wards and categories.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    # Make ward/category optional here so we can catch and refuse when they are missed
    parser.add_argument("--ward", help="Requires a specific ward.")
    parser.add_argument("--category", help="Requires a specific category.")
    parser.add_argument("--growth-type", dest="growth_type", help="Needs to be explicitly provided.")
    
    args = parser.parse_args()
    
    try:
        # Enforcement: If --growth-type not specified — refuse and ask, never guess
        if not args.growth_type:
            raise ValueError("REFUSAL: '--growth-type' was not specified. You must explicitly specify a growth type (e.g., MoM). Refusing to guess.")
            
        # Enforcement: Refuse if aggregation across wards or categories is implied (because they were omitted)
        if not args.ward or not args.category:
            raise ValueError("REFUSAL: You must strictly specify BOTH --ward and --category parameters. Aggregating across them is explicitly forbidden.")
            
        print(f"Executing Agent Pipeline for:\n  Ward: '{args.ward}'\n  Category: '{args.category}'\n  Growth Type: '{args.growth_type}'\n")
        
        # Action: Extracted skills logic
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print("No data matched the provided Ward and Category.")
            sys.exit(0)
            
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes", "growth", "formula"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"\nSUCCESS: Output written strictly to {args.output}")
            
    except Exception as e:
        print(f"\n[AI AGENT TERMINATED]: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
