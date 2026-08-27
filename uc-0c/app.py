"""
UC-0C app.py — Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os
import sys

def load_dataset(input_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and details before returning.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")
        
    data = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Check required columns
        required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column in CSV: {col}")
                
        for line_num, row in enumerate(reader, start=2):
            try:
                row["budgeted_amount"] = float(row["budgeted_amount"])
            except ValueError:
                row["budgeted_amount"] = 0.0
                
            actual_str = row.get("actual_spend", "").strip()
            if actual_str == "":
                row["actual_spend"] = None
                null_rows.append((line_num, row))
            else:
                try:
                    row["actual_spend"] = float(actual_str)
                except ValueError:
                    row["actual_spend"] = None
                    null_rows.append((line_num, row))
                    
            data.append(row)
            
    print(f"Dataset loaded successfully. Total rows: {len(data)}")
    print(f"Found {len(null_rows)} rows with null actual_spend:")
    for line_num, row in null_rows:
        print(f"  - Line {line_num}: Period={row['period']}, Ward={row['ward']}, Category={row['category']}, Reason={row['notes']}")
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters data by ward and category, calculates growth, showing formula.
    """
    if not ward or ward.strip().lower() in ["any", "all", ""]:
        print("Error: All-ward aggregation or unspecified ward is not permitted. Refusing computation.")
        sys.exit(1)
        
    if not category or category.strip().lower() in ["any", "all", ""]:
        print("Error: All-category aggregation or unspecified category is not permitted. Refusing computation.")
        sys.exit(1)
        
    if not growth_type or growth_type.strip().lower() not in ["mom", "yoy"]:
        print("Error: Growth type must be specified as 'MoM' or 'YoY'. Refusing computation.")
        sys.exit(1)
        
    filtered = [row for row in data if row["ward"] == ward and row["category"] == category]
    filtered.sort(key=lambda x: x["period"])
    
    if not filtered:
        print(f"No records found matching Ward='{ward}' and Category='{category}'.")
        return []
        
    results = []
    
    for i, current in enumerate(filtered):
        current_spend = current["actual_spend"]
        period = current["period"]
        budgeted = current["budgeted_amount"]
        notes = current["notes"]
        
        growth_rate = ""
        formula = ""
        status = "Success"
        
        if i == 0:
            status = "Skipped"
            formula = "First period in dataset (no previous month)"
            growth_rate = "n/a"
        else:
            previous = filtered[i - 1]
            prev_spend = previous["actual_spend"]
            prev_period = previous["period"]
            
            if current_spend is None:
                status = "Flagged - Null Actual Spend"
                formula = f"Cannot compute: actual_spend is null for {period} ({notes})"
                growth_rate = "NULL"
            elif prev_spend is None:
                status = "Flagged - Previous Spend Null"
                formula = f"Cannot compute: previous actual_spend ({prev_period}) is null ({previous['notes']})"
                growth_rate = "NULL"
            elif prev_spend == 0.0:
                status = "Flagged - Division by Zero"
                formula = f"Cannot compute: previous actual_spend is zero for {prev_period}"
                growth_rate = "NULL"
            else:
                diff = current_spend - prev_spend
                rate = (diff / prev_spend) * 100
                growth_rate = f"{rate:+.1f}%"
                formula = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
                
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": "NULL" if current_spend is None else current_spend,
            "growth_rate": growth_rate,
            "formula": formula,
            "status": status,
            "notes": notes
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input ward budget CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to calculate")
    parser.add_argument("--category", required=True, help="Specific budget category to calculate")
    parser.add_argument("--growth-type", required=True, help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to write the growth output CSV")
    args = parser.parse_args()
    
    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_rate", "formula", "status", "notes"]
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
                
        print(f"Growth calculation completed successfully. Output written to {args.output}")
        
    except Exception as e:
        print(f"Error executing growth calculation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
