import argparse
import csv
import sys

def load_dataset(filepath):
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows 
    before returning. Works without pandas.
    """
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if not headers:
                print("Error: Empty dataset")
                sys.exit(1)
                
            required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
            for col in required_cols:
                if col not in headers:
                    print(f"Error: Missing required column {col}")
                    sys.exit(1)
                    
            df = list(reader)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

    # Report null values before computation
    null_count = 0
    null_rows_info = []
    
    for row in df:
        val = row.get('actual_spend', '').strip()
        if not val or val.lower() == 'null':
            null_count += 1
            null_rows_info.append(row)
            
    print(f"Dataset Validation: Found {null_count} deliberate null 'actual_spend' values.")
    for row in null_rows_info:
        print(f"- Null found in: {row['period']} | {row['ward']} | {row['category']} -> Reason (Notes): {row.get('notes', '')}")
        
    return df

def compute_growth(df, ward, category, growth_type):
    """
    Skill: compute_growth
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Enforces refusal conditions outlined in agents.md.
    """
    # Enforcement Rule 4: If growth-type not specified — refuse and ask
    if not growth_type:
        print("REFUSAL: --growth-type not specified. System cannot assume or guess the aggregation method. Please explicitly provide it (e.g., MoM).")
        sys.exit(1)
        
    # Enforcement Rule 1: Never aggregate across wards or categories
    if ward.lower() in ("any", "all") or category.lower() in ("any", "all") or "," in ward or "," in category:
        print("REFUSAL: Aggregation across multiple wards or categories requested. This system only calculates strictly isolated per-ward and per-category growth.")
        sys.exit(1)

    # Isolate data by ward & category
    filtered_df = []
    for row in df:
        if row['ward'] == ward and row['category'] == category:
            filtered_df.append(row)

    if not filtered_df:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []
        
    # Sort by period ascending to calculate sequential growth
    filtered_df.sort(key=lambda x: x['period'])
    
    output_rows = []
    prev_val = None
    
    for row in filtered_df:
        period = row['period']
        budgeted = row['budgeted_amount']
        actual_raw = row.get('actual_spend', '').strip()
        notes = row.get('notes', '').strip()
        
        # Enforcement Rule 2: Flag every null row before computing
        if not actual_raw or actual_raw.lower() == 'null':
            growth_str = f"Must be flagged — not computed. Reason: {notes}"
            actual_str = "NULL"
            formula_str = "N/A - Null actual_spend"
            prev_val = None # Breaks continuity 
        else:
            try:
                actual = float(actual_raw)
            except ValueError:
                print(f"Error: Non-numeric active_spend '{actual_raw}' found.")
                sys.exit(1)
                
            actual_str = str(actual)
            
            if growth_type.lower() == "mom":
                if prev_val is not None:
                    growth_val = ((actual - prev_val) / prev_val) * 100
                    sign = "+" if growth_val > 0 else "-" if growth_val < 0 else ""
                    growth_str = f"{sign}{abs(growth_val):.1f}%"
                    if notes:
                        growth_str += f" ({notes})"
                    
                    # Enforcement Rule 3: Show formula used
                    formula_str = f"({actual} - {prev_val}) / {prev_val} * 100"
                else:
                    growth_str = "n/a"
                    formula_str = "N/A - No previous valid period"
                prev_val = actual
            else:
                growth_str = "Calculation not implemented for this growth type"
                formula_str = "N/A"
                
        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            # we need to keep "actual_spend" matching output instructions, "NULL" vs numeric
            "actual_spend": actual_str,
            "calculated_growth": growth_str,
            "formula": formula_str
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Growth Tool")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Target ward for isolated calculation")
    parser.add_argument("--category", required=True, help="Target category for isolated calculation")
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g. MoM). If absent, system will refuse.")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    args = parser.parse_args()

    # Step 1: Load and validate dataset
    df = load_dataset(args.input)
    
    # Step 2: Extract target metrics
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    # Step 3: Write out output
    if result_df:
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "calculated_growth", "formula"]
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in result_df:
                writer.writerow(row)
                
        print(f"Success! Output written to {args.output}")

if __name__ == "__main__":
    main()
