"""
UC-0C — Number That Looks Right
Rule-based implementation simulating a Financial Analyst AI enforcing CRAFT constraints.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str):
    """Reads CSV and returns rows. Analyzes nulls."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

def compute_growth(rows, ward, category, growth_type, output_path):
    # Enforcement 1 & 4: Refusals
    if not ward or not category:
        print("REFUSAL: Cannot aggregate across wards or categories. Please specify exact --ward and --category.")
        sys.exit(1)
    if not growth_type:
        print("REFUSAL: --growth-type not specified. I cannot guess the formula. Please specify (e.g., MoM).")
        sys.exit(1)
        
    if growth_type.upper() != "MOM":
        print(f"REFUSAL: Only MoM is currently supported, got {growth_type}")
        sys.exit(1)

    # Filter data
    filtered = [r for r in rows if r.get('ward') == ward and r.get('category') == category]
    
    if not filtered:
        print(f"No data found for Ward: {ward}, Category: {category}")
        sys.exit(1)
        
    # Sort by period to compute safely
    filtered.sort(key=lambda x: x.get('period', ''))
    
    # Process rows
    results = []
    prev_spend = None
    
    for row in filtered:
        actual_spend_str = row.get('actual_spend', '').strip()
        period = row.get('period', '')
        actual_spend = None
        notes = row.get('notes', '')
        
        # New fields
        growth_perc = ""
        formula = ""
        flag_note = ""
        
        # Enforcement 2: Flag null rows
        if not actual_spend_str or actual_spend_str.upper() == "NULL":
            flag_note = f"NULL DETECTED: {notes}"
            prev_spend = None # Cannot compute next month safely either if missing data
        else:
            try:
                actual_spend = float(actual_spend_str)
            except ValueError:
                flag_note = "INVALID NUMBER"
                prev_spend = None
                
        if actual_spend is not None:
            if prev_spend is not None:
                # Enforcement 3: Show formula used
                growth = ((actual_spend - prev_spend) / prev_spend) * 100
                growth_perc = f"{growth:+.1f}%"
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend} * 100"
            else:
                growth_perc = "n/a"
                formula = "No previous month data"
            
            prev_spend = actual_spend
        else:
            growth_perc = "NULL"
            formula = "Cannot compute on NULL"

        
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'budgeted_amount': row.get('budgeted_amount', ''),
            'actual_spend': actual_spend_str,
            'growth_percentage': growth_perc,
            'formula_used': formula,
            'flag_note': flag_note
        })
        
    # Write output
    fieldnames = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'growth_percentage', 'formula_used', 'flag_note']
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Success. Wrote {len(results)} rows to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward to filter")
    parser.add_argument("--category", required=False, help="Specific category to filter")
    parser.add_argument("--growth-type", required=False, help="Formula type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()
    
    rows = load_dataset(args.input)
    compute_growth(rows, args.ward, args.category, args.growth_type, args.output)
