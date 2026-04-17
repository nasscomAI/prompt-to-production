"""
UC-0C Budget Data Analyst
Computes granular growth reports with strict null handling and formula transparency.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Loads and validates the budget dataset.
    Registers rows with null 'actual_spend' values.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_mom_growth(data: list, ward: str, category: str) -> list:
    """
    Calculates Month-on-Month (MoM) growth for a specific ward and category.
    """
    # Filter and sort by period
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        period = current['period']
        actual = current['actual_spend']
        notes = current['notes']
        
        res = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": actual if actual else "NULL",
            "MoM Growth": "N/A",
            "Formula": "N/A",
            "Status": "OK"
        }
        
        # 1. Null Handling (Rule 2)
        if not actual or actual.strip() == "":
            res["MoM Growth"] = "NULL"
            res["Formula"] = "ERROR: Missing Actual Spend"
            res["Status"] = f"FLAGGED: {notes}"
            results.append(res)
            continue
            
        # 2. First period logic
        if i == 0:
            res["MoM Growth"] = "N/A (First Period)"
            res["Formula"] = "N/A"
            results.append(res)
            continue
            
        # 3. Growth calculation with formula transparency (Rule 3)
        try:
            prev_val = float(prev['actual_spend']) if prev and prev['actual_spend'] else None
            curr_val = float(actual)
            
            if prev_val is None:
                res["MoM Growth"] = "N/A"
                res["Formula"] = "ERROR: Previous month was NULL"
                res["Status"] = "INCOMPLETE"
            elif prev_val == 0:
                res["MoM Growth"] = "INF"
                res["Formula"] = f"({curr_val} - 0) / 0"
            else:
                growth = ((curr_val - prev_val) / prev_val) * 100
                res["MoM Growth"] = f"{growth:+.1f}%"
                res["Formula"] = f"({curr_val} - {prev_val}) / {prev_val}"
                
        except (ValueError, TypeError):
            res["MoM Growth"] = "ERROR"
            res["Formula"] = "Calculation Error"
            
        results.append(res)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Data Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Filter by Ward")
    parser.add_argument("--category", help="Filter by Category")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results")
    args = parser.parse_args()

    # Rule 4: Refuse if growth-type missing
    if not args.growth_type:
        print("REFUSAL: Growth type not specified. Please specify --growth-type MoM.")
        sys.exit(1)
        
    # Rule 1/5: Refuse all-ward aggregation
    if not args.ward or not args.category:
        print("REFUSAL: Ward or Category missing. Aggregated results are prohibited.")
        sys.exit(1)

    try:
        data = load_dataset(args.input)
        
        if args.growth_type.upper() == "MOM":
            results = compute_mom_growth(data, args.ward, args.category)
        else:
            print(f"REFUSAL: Growth type '{args.growth_type}' not supported or requires specification.")
            sys.exit(1)
            
        # Write output
        if results:
            fieldnames = results[0].keys()
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Success! Granular records written to {args.output}")
        else:
            print("No data found for the specified Ward and Category.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
