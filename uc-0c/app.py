"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning"""
    data = []
    null_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            expected_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not expected_cols.issubset(set(reader.fieldnames)):
                print(f"Error: Missing expected columns. Found: {reader.fieldnames}")
                sys.exit(1)
                
            for row in reader:
                data.append(row)
                if not row['actual_spend'].strip():
                    null_rows.append(row)
    except Exception as e:
        print(f"Error loading CSV {filepath}: {e}")
        sys.exit(1)
        
    if null_rows:
        print(f"System Check: Detected {len(null_rows)} null actual_spend rows:")
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} -> Reason: {r['notes']}")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward + category + growth_type, returns per-period table with formula shown"""
    
    if not growth_type:
        print("Refusal: --growth-type not specified. I cannot guess the requested growth formula. Please provide it.")
        sys.exit(1)
        
    if not ward or not category:
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed. Please provide specific --ward and --category.")
        sys.exit(1)
        
    # Filter dataset strictly
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort chronologically
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    previous_spend = None
    
    for row in filtered_data:
        actual_spend_str = row['actual_spend'].strip()
        
        if not actual_spend_str:
            results.append({
                "Ward": row['ward'],
                "Category": row['category'],
                "Period": row['period'],
                "Actual Spend (₹ lakh)": "NULL",
                "MoM Growth": f"Must be flagged — not computed (Reason: {row['notes']})"
            })
            previous_spend = None # Reset due to missing data block
            continue
            
        current_spend = float(actual_spend_str)
        
        if previous_spend is None:
            results.append({
                "Ward": row['ward'],
                "Category": row['category'],
                "Period": row['period'],
                "Actual Spend (₹ lakh)": current_spend,
                "MoM Growth": "n/a (Formula: No previous data)"
            })
        else:
            if growth_type.lower() == 'mom':
                if previous_spend == 0:
                    growth_val = "Infinity"
                else:
                    growth_pct = ((current_spend - previous_spend) / previous_spend) * 100
                    # Standardize sign presentation
                    sign = "+" if growth_pct > 0 else "−" if growth_pct < 0 else ""
                    rounded = abs(growth_pct)
                    growth_val = f"{sign}{rounded:.1f}%"
                    
                formula = f"(({current_spend} - {previous_spend}) / {previous_spend}) * 100"
                
                results.append({
                    "Ward": row['ward'],
                    "Category": row['category'],
                    "Period": row['period'],
                    "Actual Spend (₹ lakh)": current_spend,
                    "MoM Growth": f"{growth_val} (Formula: {formula})"
                })
            else:
                print(f"Refusal: Unknown growth-type '{growth_type}'. Cannot compute.")
                sys.exit(1)
                
        previous_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input budget csv")
    parser.add_argument("--ward", required=False, help="Ward name constraint")
    parser.add_argument("--category", required=False, help="Category name constraint")
    parser.add_argument("--growth-type", required=False, help="Growth metric")
    parser.add_argument("--output", required=True, help="Path to output csv")
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    try:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing to {args.output}: {e}")

if __name__ == "__main__":
    main()
