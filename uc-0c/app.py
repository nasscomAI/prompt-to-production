"""
UC-0C Budget Growth Calculator
Implemented using RICE framework, agents.md, and skills.md.
"""
import argparse
import csv
import os

def load_dataset(input_path):
    """
    Skill: load_dataset
    Reads the budget CSV and pre-identifies null values in actual_spend.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget CSV not found at: {input_path}")
    
    data = []
    null_count = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check for mandatory columns
        required = {'period', 'ward', 'category', 'actual_spend', 'notes'}
        if not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing mandatory columns. Expected: {required}")
            
        for row in reader:
            # Pre-identify null values
            raw_spend = row.get('actual_spend', '').strip()
            if raw_spend == "":
                row['actual_spend'] = None
                null_count += 1
            else:
                try:
                    row['actual_spend'] = float(raw_spend)
                except ValueError:
                    row['actual_spend'] = None
                    null_count += 1
            
            data.append(row)
    
    print(f"Dataset loaded. Total rows: {len(data)}. Null actual_spend values found: {null_count}.")
    return data

def compute_growth(data, target_ward=None, target_category=None, growth_type="MoM"):
    """
    Skill: compute_growth
    Calculates growth metrics. If ward/category are not provided, processes the entire dataset
    group-by-group to prevent unauthorized aggregation.
    """
    # Identify unique combinations to process
    if target_ward and target_category:
        combinations = [(target_ward, target_category)]
    else:
        # Get all unique ward-category pairs
        combinations = sorted(list(set((r['ward'], r['category']) for r in data)))
    
    all_results = []
    
    for ward, category in combinations:
        # Filter for the specific group
        filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
        
        # Chronological sort for MoM
        filtered.sort(key=lambda x: x['period'])
        
        for i, current in enumerate(filtered):
            res = {
                "period": current['period'],
                "ward": current['ward'],
                "category": current['category'],
                "actual_spend": current['actual_spend'] if current['actual_spend'] is not None else "NULL",
                "growth": "n/a",
                "formula": "n/a",
                "flag": ""
            }
            
            # Enforcement 2: Flag null rows before computing
            if current['actual_spend'] is None:
                res['flag'] = f"NULL: {current['notes']}"
                all_results.append(res)
                continue
                
            if i > 0:
                previous = filtered[i-1]
                if previous['actual_spend'] is not None:
                    curr_val = current['actual_spend']
                    prev_val = previous['actual_spend']
                    
                    # Calculation logic
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    res['growth'] = f"{growth:+.1f}%"
                    
                    # Enforcement 3: Show formula
                    res['formula'] = f"({curr_val} - {prev_val}) / {prev_val}"
                else:
                    res['flag'] = "Cannot compute growth: Previous period data is NULL"
            else:
                res['formula'] = "Baseline period (first in sequence)"
                
            all_results.append(res)
        
    return all_results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Budget Data Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Target Ward name (optional)")
    parser.add_argument("--category", default=None, help="Target budget category (optional)")
    parser.add_argument("--growth-type", required=True, help="Type of growth calculation (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    # Enforcement 1: Refuse general aggregations (summing up multiple wards)
    if args.ward and args.ward.lower() in ["all", "any"] and not args.category:
        print("ERROR: Unauthorized aggregation detected. The system refuses to sum data across multiple wards into a single total.")
        return

    try:
        # Step 1: Load and Validate
        dataset = load_dataset(args.input)
        
        # Step 2: Compute
        # If ward/category are None, compute_growth will process all groups individually
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        if not results:
            print("No matching data found for the specified filters.")
            return
            
        # Step 3: Write Output
        fieldnames = results[0].keys()
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Full dataset analysis complete. Output written to {args.output}")

    except Exception as e:
        print(f"PIPELINE_ERROR: {str(e)}")


if __name__ == "__main__":
    main()
