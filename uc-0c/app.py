"""
UC-0C app.py — Budget Analysis Assistant Implementation.
Calculates ward-level growth while strictly enforcing granular reporting and null-value flagging.
"""
import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """Skill: Reads and validates the budget CSV dataset."""
    if not os.path.exists(file_path):
        print(f"Error: Dataset not found at {file_path}")
        sys.exit(1)
    
    data = []
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not required_cols.issubset(set(reader.fieldnames)):
            print(f"Error: Dataset missing required columns. Found: {reader.fieldnames}")
            sys.exit(1)
        
        for row in reader:
            data.append(row)
    return data

def compute_growth(ward, category, growth_type, dataset):
    """Skill: Calculates MoM/YoY growth with formula tracking and null-flagging."""
    # Filter data - Refusal to aggregate is implied by specific filtering
    filtered = [r for r in dataset if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.")
        return []
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    output_rows = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        curr_val_str = current['actual_spend'].strip()
        curr_val = float(curr_val_str) if curr_val_str else None
        
        # Determine previous period based on growth_type
        prev_row = None
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
        elif growth_type == "YoY":
            curr_period = current['period'] # YYYY-MM
            try:
                year, month = map(int, curr_period.split('-'))
                prev_year_period = f"{year-1}-{month:02d}"
                prev_row = next((r for r in filtered if r['period'] == prev_year_period), None)
            except ValueError:
                prev_row = None
        
        prev_val_str = prev_row['actual_spend'].strip() if prev_row else ""
        prev_val = float(prev_val_str) if prev_val_str else None
        
        growth_result = "n/a"
        formula = "n/a"
        status = "OK"
        null_reason = current['notes'] if not curr_val_str else "n/a"
        
        if curr_val is None:
            growth_result = "NULL"
            status = "FLAGGED"
            formula = f"Cannot compute {growth_type} - Current period value is missing"
        elif prev_val is None:
            growth_result = "NULL"
            status = "FLAGGED"
            if prev_row:
                formula = f"Cannot compute {growth_type} - Previous period ({prev_row['period']}) value is missing"
            else:
                formula = f"First period in series - No previous data for {growth_type}"
        else:
            diff = curr_val - prev_val
            growth = (diff / prev_val) * 100 if prev_val != 0 else 0
            growth_result = f"{growth:+.1f}%"
            formula = f"({curr_val} - {prev_val}) / {prev_val}"
            
        output_rows.append({
            "period": current['period'],
            "ward": current['ward'],
            "category": current['category'],
            "actual_spend": current['actual_spend'] or "NULL",
            "growth": growth_result,
            "formula": formula,
            "status": status,
            "null_reason": null_reason
        })
        
    return output_rows

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    # Enforcement 4: Refuse if --growth-type not specified
    if not args.growth_type:
        print("Error: --growth-type was not specified. Refusing to proceed. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    results = compute_growth(args.ward, args.category, args.growth_type, dataset)
    
    if results:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "status", "null_reason"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Success: Report generated at {args.output}")

if __name__ == "__main__":
    main()
