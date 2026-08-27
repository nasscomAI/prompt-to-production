"""
UC-0C app.py — Agent implementation strictly conforming to agents.md and skills.md.
"""
import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Skill: load_dataset
    Reads the provided CSV dataset, validates required columns, and flags any rows containing null
    actual_spend values along with their notes before returning the data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    data = []
    null_count = 0
    null_rows = []

    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = [h.strip() if h else h for h in (reader.fieldnames or [])]
        
        for col in required_columns:
            if col not in headers:
                raise ValueError(f"Missing required column: {col}")
        
        for row in reader:
            val = row.get('actual_spend', '').strip()
            if not val or val.lower() == 'null':
                null_count += 1
                null_rows.append((row.get('period'), row.get('ward'), row.get('category'), row.get('notes')))
            data.append(row)
            
    print(f"[load_dataset] Successfully loaded {len(data)} rows.")
    print(f"[load_dataset] FLAGGED: Found {null_count} rows with null 'actual_spend'.")
    for period, ward, cat, notes in null_rows:
        print(f"  -> Null at Period: {period} | Ward: {ward} | Category: {cat} | Reason: {notes}")
        
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Calculates localized spend growth metrics for a specific ward and category without unauthorized
    cross-aggregation, actively reporting null reasons.
    """
    # ENFORCEMENT 4: If `--growth-type` not specified — refuse and ask, never guess
    if not growth_type:
        raise ValueError("growth-type parameter missing. I refuse to guess whether to compute MoM or YoY.")
        
    growth_type = growth_type.upper()
    if growth_type not in ["MOM", "YOY"]:
        raise ValueError(f"Unknown growth-type '{growth_type}'. Please specify MoM or YoY.")
        
    # ENFORCEMENT 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or not category or ward.lower() == "any" or category.lower() == "any":
        raise ValueError("Refusing to aggregate across all wards or categories. Please provide a specific ward and category.")
        
    # Filter dataset strictly to operational boundaries
    filtered = [row for row in data if row.get('ward') == ward and row.get('category') == category]
    
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        
    # Sort chronologically by period
    filtered.sort(key=lambda x: x.get('period', ''))
    
    results = []
    
    for i in range(len(filtered)):
        row = filtered[i]
        period = row.get('period')
        budgeted = row.get('budgeted_amount')
        actual_str = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        
        out_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': budgeted,
            'actual_spend': actual_str,
            'growth_metric': '',
            'formula_used': '',
            'flag': ''
        }
        
        # ENFORCEMENT 2: Flag every null row before computing — report null reason from the notes column
        if not actual_str or actual_str.lower() == 'null':
            out_row['growth_metric'] = 'NULL'
            out_row['formula_used'] = 'Not computed - null value flagged'
            out_row['flag'] = f"Null Reason: {notes}"
            results.append(out_row)
            continue
            
        current_val = float(actual_str)
        prev_val = None
        formula = ""
        
        # Calculate metric based on type
        if growth_type == "MOM":
            if i > 0:
                prev_actual_str = filtered[i-1].get('actual_spend', '').strip()
                if prev_actual_str and prev_actual_str.lower() != 'null':
                    prev_val = float(prev_actual_str)
                    # ENFORCEMENT 3: Show formula used in every output row alongside the result
                    formula = f"(({current_val} - {prev_val}) / abs({prev_val})) * 100"
                else:
                    formula = "Previous month actual_spend is NULL"
            else:
                formula = "No previous month available in query"
                
        elif growth_type == "YOY":
            try:
                curr_year, curr_month = map(int, period.split('-'))
                prev_year_period = f"{curr_year-1}-{curr_month:02d}"
                
                prev_match = [r for r in filtered if r.get('period') == prev_year_period]
                if prev_match:
                    prev_actual_str = prev_match[0].get('actual_spend', '').strip()
                    if prev_actual_str and prev_actual_str.lower() != 'null':
                        prev_val = float(prev_actual_str)
                        formula = f"(({current_val} - {prev_val}) / abs({prev_val})) * 100"
                    else:
                        formula = "Previous year actual_spend is NULL"
                else:
                    formula = "No previous year available in query"
            except ValueError:
                formula = "Invalid period format for YoY calculation"
                
        if prev_val is not None:
            if prev_val == 0:
                out_row['growth_metric'] = 'Infinity'
            else:
                growth = ((current_val - prev_val) / abs(prev_val)) * 100
                out_row['growth_metric'] = f"{growth:+.1f}%"
        else:
            out_row['growth_metric'] = 'N/A'
            
        out_row['formula_used'] = formula
        results.append(out_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Data Analyst Agent")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to analyze")
    parser.add_argument("--category", required=False, help="Specific category to analyze")
    parser.add_argument("--growth-type", required=False, help="Type of growth calculation (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to write the results CSV")
    
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        # Write results identically formatted to requirements
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_metric', 'formula_used', 'flag']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"[Agent] successfully generated strict per-ward table at {args.output}")
        
    except Exception as e:
        print(f"\n[AGENT REFUSAL] {str(e)}\n", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
