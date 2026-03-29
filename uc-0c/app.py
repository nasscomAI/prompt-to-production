"""
UC-0C app.py — Number That Looks Right
Implemented strictly using the RICE framework.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str, ward: str, category: str) -> list:
    """
    Reads the CSV dataset and enforces boundaries by strictly extracting only 
    the targeted ward and category slice. It will outright refuse 'Any' parameters.
    Explicitly tracks parsing logic for missing actual_spend.
    """
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        raise ValueError("REFUSAL: Cannot aggregate across multiple wards or categories explicitly or implicitly. Please specify exact targets.")
        
    filtered_data = []
    null_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ward'] == ward and row['category'] == category:
                    spend_str = row['actual_spend'].strip()
                    if not spend_str:
                        row['actual_spend'] = None  # Identify explicit omission 
                        null_count += 1
                    else:
                        try:
                            row['actual_spend'] = float(spend_str)
                        except ValueError:
                            row['actual_spend'] = None
                            null_count += 1
                    filtered_data.append(row)
    except FileNotFoundError:
        raise ValueError(f"Error: Could not find file {input_path}")
        
    if not filtered_data:
        raise ValueError(f"No data found for Ward '{ward}' and Category '{category}'.")
        
    print(f"Loaded {len(filtered_data)} rows safely for computation window. Intercepted {null_count} nulls.")
    
    # Chronological sort required for period metrics
    filtered_data.sort(key=lambda x: x['period'])
    return filtered_data


def compute_growth(data: list, growth_type: str) -> list:
    """
    Computes strict metrics while preserving formula visibility, rejecting unspecified calculations, 
    and enforcing null boundaries instead of treating omissions as 0.0.
    """
    if not growth_type or growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"REFUSAL: Invalid or unspecified growth type '{growth_type}'. Cannot silently assume or hallucinate formula logic.")
        
    formula_str = f"{growth_type}: ((current - previous) / previous * 100)"
    results = []
    
    for i in range(len(data)):
        current_row = data[i]
        period = current_row['period']
        current_spend = current_row['actual_spend']
        notes = current_row.get('notes', '').strip()
        
        # Step back index
        prev_idx = i - 1 if growth_type == 'MoM' else i - 12
        
        if prev_idx < 0:
            growth_val = "n/a (no previous period baseline)"
        else:
            prev_row = data[prev_idx]
            prev_spend = prev_row['actual_spend']
            
            # Critical Enforcement Rule: Silence Null Aggregation
            if current_spend is None or prev_spend is None:
                reason = current_row.get('notes') if current_spend is None else prev_row.get('notes', 'Missing baseline data')
                growth_val = f"Must be flagged — not computed. Null reason: {reason}"
            else:
                if prev_spend == 0:
                    growth_val = "n/a (division by zero)"
                else:
                    growth_rate = ((current_spend - prev_spend) / prev_spend) * 100
                    # Format requirement from references
                    sign = "+" if growth_rate > 0 else ""
                    note_suffix = f" ({notes})" if notes else ""
                    growth_val = f"{sign}{growth_rate:.1f}%{note_suffix}"
                    
        spend_display = current_spend if current_spend is not None else "NULL"
        
        results.append({
            "period": period,
            "ward": current_row['ward'],
            "category": current_row['category'],
            "actual_spend": spend_display,
            "growth": growth_val,
            "formula_enforced": formula_str
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input dataset via CSV")
    parser.add_argument("--ward", required=False, default=None, help="Target precise ward")
    parser.add_argument("--category", required=False, default=None, help="Target precise category")
    parser.add_argument("--growth-type", required=False, default=None, help="Growth logic ('MoM' or 'YoY')")
    parser.add_argument("--output", required=True, help="Path for generated structured output")
    
    args = parser.parse_args()
    
    try:
        # Step 1: Secure Data Retrieval
        data = load_dataset(args.input, args.ward, args.category)
        
        # Step 2: RICE-Strict Computation
        calc_out = compute_growth(data, args.growth_type)
        
        # Persist File
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula_enforced"]
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(calc_out)
            
        print(f"Data reliably aggregated. Safely exported to {args.output}")

    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
