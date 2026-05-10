"""
UC-0C app.py — Budget Growth Calculator
Implemented using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """
    Reads the budget CSV, validates columns, and reports the null count and specific null rows before returning the data.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
        
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_cols.issubset(set(reader.fieldnames or [])):
        print(f"Error: Missing required columns. Found {reader.fieldnames}")
        sys.exit(1)

    null_rows = [r for r in rows if not r.get('actual_spend', '').strip()]
    print(f"Dataset loaded. Found {len(null_rows)} deliberate null actual_spend rows:")
    for r in null_rows:
        print(f" - {r['period']} | {r['ward']} | {r['category']} | Reason: {r['notes']}")
        
    return rows

def compute_growth(dataset: list, ward: str, category: str, growth_type: str):
    """
    Computes growth per period for a specific ward and category, returning a table with formulas shown.
    Enforces rules to not aggregate across wards/categories and not guess the growth type.
    """
    if not growth_type:
        raise ValueError("Refusal: --growth-type not specified. Please specify MoM or YoY, never guess.")
        
    if not ward or not category or ward.lower() == 'any' or category.lower() == 'any':
        raise ValueError("Refusal: Never aggregate across wards or categories unless explicitly instructed. Please specify an exact ward and category.")
        
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row['notes']
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_str if actual_str else "NULL",
            'growth': "NULL",
            'formula': "N/A"
        }
        
        if not actual_str:
            result_row['formula'] = f"Skipped (Null actual_spend): {notes}"
            prev_spend = None
        else:
            current_spend = float(actual_str)
            if prev_spend is None:
                result_row['formula'] = "No previous period data to compare"
            else:
                if growth_type.upper() == 'MOM':
                    growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                    sign = "+" if growth_val > 0 else ""
                    result_row['growth'] = f"{sign}{growth_val:.1f}%"
                    result_row['formula'] = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                else:
                    result_row['formula'] = f"Formula for {growth_type} not implemented in this demo"
            
            prev_spend = current_spend
            
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write output csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    
    try:
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(e)
        sys.exit(1)
        
    if not results:
        print("No matching data found for the specified ward and category.")
        sys.exit(1)
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula']
    
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth calculation successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
