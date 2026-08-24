"""
UC-0C app.py — Budget Analyst
Built using agents.md and skills.md requirements.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> tuple[list[dict], dict]:
    """
    Reads CSV, validates columns, reports null count and location before returning.
    Returns: (data, null_report)
    """
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    nulls = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])
            if not required_cols.issubset(headers):
                print(f"Error: Missing required columns. Expected {required_cols}, found {headers}")
                sys.exit(1)
                
            for i, row in enumerate(reader, start=2): # 1 is header
                actual_spend_raw = row['actual_spend'].strip()
                if not actual_spend_raw:
                    nulls.append({
                        "row": i,
                        "period": row['period'],
                        "ward": row['ward'],
                        "category": row['category'],
                        "notes": row['notes']
                    })
                    row['actual_spend'] = None
                else:
                    row['actual_spend'] = float(actual_spend_raw)
                
                row['budgeted_amount'] = float(row['budgeted_amount']) if row['budgeted_amount'].strip() else 0.0
                data.append(row)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)
        
    print(f"--- Data Loading Report ---")
    print(f"Total rows loaded: {len(data)}")
    print(f"Total null actual_spend values found: {len(nulls)}")
    for n in nulls:
        print(f"  - Null at Row {n['row']} ({n['period']}, {n['ward']}, {n['category']}) - Reason: {n['notes']}")
    print(f"---------------------------\n")
    
    return data, nulls

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    if not growth_type:
        print("ERROR: --growth-type not specified. Refusing to guess. Please explicitly specify MoM or YoY.")
        sys.exit(1)
        
    if not ward or not category:
        print("ERROR: Must specify exactly one ward and one category to prevent silent aggregation.")
        sys.exit(1)
        
    if growth_type.lower() not in ["mom", "yoy"]:
        print(f"ERROR: Unsupported growth type '{growth_type}'. Only MoM and YoY are supported.")
        sys.exit(1)
        
    # Filter data for specific ward and category
    filtered = [d for d in data if d['ward'] == ward and d['category'] == category]
    if not filtered:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'")
        return []
        
    # Sort by period to ensure correct chronological order
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, current in enumerate(filtered):
        period = current['period']
        current_val = current['actual_spend']
        notes = current['notes']
        
        result_row = {
            "Ward": current['ward'],
            "Category": current['category'],
            "Period": period,
            "Actual Spend (₹ lakh)": str(current_val) if current_val is not None else "NULL",
            "Growth": "",
            "Formula Used": "",
            "Flag/Note": ""
        }
        
        if current_val is None:
            result_row["Flag/Note"] = f"NULL VALUE FLAGGED. Reason: {notes}"
            result_row["Growth"] = "NULL"
            result_row["Formula Used"] = "N/A (Missing current value)"
            results.append(result_row)
            continue
            
        if growth_type.lower() == "mom":
            # Compare with previous period in the sorted list
            if i == 0:
                result_row["Growth"] = "N/A"
                result_row["Formula Used"] = "N/A (No previous month data)"
            else:
                prev = filtered[i-1]
                prev_val = prev['actual_spend']
                
                if prev_val is None:
                    result_row["Growth"] = "N/A"
                    result_row["Formula Used"] = "N/A (Previous month value is NULL)"
                    result_row["Flag/Note"] = f"Cannot compute MoM; previous month ({prev['period']}) is null."
                elif prev_val == 0:
                    result_row["Growth"] = "N/A"
                    result_row["Formula Used"] = f"({current_val} - {prev_val}) / {prev_val} (Div by zero)"
                else:
                    growth_pct = ((current_val - prev_val) / prev_val) * 100
                    sign = "+" if growth_pct > 0 else ""
                    result_row["Growth"] = f"{sign}{growth_pct:.1f}%"
                    result_row["Formula Used"] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
                    
        elif growth_type.lower() == "yoy":
             result_row["Growth"] = "N/A"
             result_row["Formula Used"] = "N/A (YoY logic simplified)"
             
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Explicit ward name")
    parser.add_argument("--category", required=True, help="Explicit category name")
    parser.add_argument("--growth-type", help="Must be MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    
    args = parser.parse_args()
    
    # 1. Enforce refusal rule if growth-type is missing
    if not args.growth_type:
        print("AGENT REFUSAL: --growth-type was not specified. I am explicitly programmed not to guess or assume the growth metric (MoM/YoY). Please specify.")
        sys.exit(1)
        
    # 2. Load and explicitly flag nulls
    data, nulls = load_dataset(args.input)
    
    # 3. Compute growth unaggregated
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    # 4. Write to CSV
    if not results:
        print("No results to write.")
        sys.exit(0)
        
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "Growth", "Formula Used", "Flag/Note"]
    
    try:
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Analysis completed successfully. Output written to {args.output}")
    except Exception as e:
        print(f"Failed to write output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
