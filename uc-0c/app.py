"""
UC-0C — Budget Growth Calculator
Implementation based on agents.md and skills.md.
"""
import argparse
import csv
import os

def load_dataset(input_path: str):
    """
    Reads the CSV and reports null rows.
    """
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return None
        
    data = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Check for null in actual_spend
            if not row['actual_spend'] or row['actual_spend'].strip().lower() == 'null':
                null_rows.append({
                    'line': i + 2,
                    'period': row['period'],
                    'ward': row['ward'],
                    'category': row['category'],
                    'notes': row['notes']
                })
                row['actual_spend'] = None
            else:
                try:
                    row['actual_spend'] = float(row['actual_spend'])
                except ValueError:
                    row['actual_spend'] = None
            data.append(row)
            
    if null_rows:
        print(f"IDENTIFIED {len(null_rows)} NULL ROWS IN DATASET:")
        for nr in null_rows:
            print(f" - {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
            
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Computes MoM growth for a specific ward and category.
    """
    # 1. Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"Error: No data found for Ward: {ward}, Category: {category}")
        return []
        
    # 2. Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        curr_spend = row['actual_spend']
        period = row['period']
        growth_value = "n/a"
        formula = "n/a"
        flag = ""
        
        if curr_spend is None:
            growth_value = "[DATA_MISSING]"
            formula = "n/a"
            flag = row['notes']
        elif prev_spend is None and results:
            # Previous was null
            growth_value = "[DATA_MISSING]"
            formula = f"({curr_spend} - NULL) / NULL"
            flag = "Previous month data is missing"
        elif prev_spend is not None:
            # Compute growth
            # MoM = (Current - Previous) / Previous
            if prev_spend == 0:
                 growth_value = "inf"
                 formula = f"({curr_spend} - 0) / 0"
            else:
                diff = curr_spend - prev_spend
                growth = (diff / prev_spend) * 100
                growth_value = f"{growth:+.1f}%"
                formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
        else:
            # First row
            formula = "First period (no previous data)"
            
        results.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': curr_spend if curr_spend is not None else "NULL",
            'growth': growth_value,
            'formula': formula,
            'notes': flag
        })
        
        prev_spend = curr_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # ENFORCEMENT RULES
    if not args.growth_type:
        print("REFUSAL: Growth type (MoM, YoY) must be explicitly specified. Please provide --growth-type.")
        return
        
    print(f"Loading dataset: {args.input}")
    data = load_dataset(args.input)
    if not data:
        return
        
    all_results = []
    
    if args.ward and args.category:
        print(f"Computing {args.growth_type} for Ward: {args.ward}, Category: {args.category}")
        all_results = compute_growth(data, args.ward, args.category, args.growth_type)
    else:
        # Process all unique ward/category combinations independently (No aggregation)
        print(f"Processing all wards and categories independently for {args.growth_type} analysis...")
        wards = sorted(list(set(row['ward'] for row in data)))
        categories = sorted(list(set(row['category'] for row in data)))
        
        for w in wards:
            for c in categories:
                results = compute_growth(data, w, c, args.growth_type)
                all_results.extend(results)
    
    if all_results:
        fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Analysis complete. Results saved to: {args.output}")

if __name__ == "__main__":
    main()
