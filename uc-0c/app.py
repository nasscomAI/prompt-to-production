"""
UC-0C app.py — Budget Data Analyst
"""
import argparse
import csv
import os

def calculate_growth(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ward'] == ward and row['category'] == category:
                data.append(row)

    if not data:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return

    results = []
    prev_spend = None
    
    for i, row in enumerate(data):
        period = row['period']
        actual_str = row['actual_spend']
        notes = row['notes']
        
        if not actual_str or actual_str.strip() == "":
            result_row = {
                "Period": period,
                "Ward": ward,
                "Category": category,
                "Actual Spend": "NULL",
                "Formula": "n/a",
                "Result": f"FLAGGED: {notes}"
            }
            prev_spend = None # Cannot calculate growth from/to null
        else:
            actual_spend = float(actual_str)
            if prev_spend is not None and growth_type == "MoM":
                growth = ((actual_spend - prev_spend) / prev_spend) * 100
                formula = f"({actual_spend} - {prev_spend}) / {prev_spend}"
                result_str = f"{growth:+.1f}%"
            else:
                formula = "n/a (First data point or null prev)"
                result_str = "n/a"
            
            result_row = {
                "Period": period,
                "Ward": ward,
                "Category": category,
                "Actual Spend": actual_spend,
                "Formula": formula,
                "Result": result_str
            }
            prev_spend = actual_spend
            
        results.append(result_row)

    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["Period", "Ward", "Category", "Actual Spend", "Formula", "Result"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Data Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    calculate_growth(args.input, args.ward, args.category, args.growth_type, args.output)
    print(f"Done. Growth report written to {args.output}")
