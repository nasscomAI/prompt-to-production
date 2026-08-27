"""
UC-0C — Number That Looks Right
AI budget analysis agent for granular growth computation and data integrity.
"""
import argparse
import csv
import os
import sys
from datetime import datetime

def load_dataset(path: str) -> list:
    """
    Skill: load_dataset
    Reads CSV, validates required columns, reports null count and identifies 
    specific null rows with their notes before returning.
    """
    if not os.path.exists(path):
        print(f"Error: Input file '{path}' not found.")
        sys.exit(1)
    
    data = []
    null_rows_detected = []
    
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print("Error: Input file is empty or headers are missing.")
                sys.exit(1)
            
            # Column Validation
            missing = [col for col in required_columns if col not in reader.fieldnames]
            if missing:
                print(f"Error: Missing required columns: {missing}")
                sys.exit(1)
            
            for row in reader:
                # Check for null actual_spend
                actual_val = (row.get('actual_spend') or "").strip()
                if not actual_val:
                    null_rows_detected.append({
                        "period": row.get('period'),
                        "ward": row.get('ward'),
                        "category": row.get('category'),
                        "reason": row.get('notes')
                    })
                data.append(row)
                
    except Exception as e:
        print(f"Error: Failed to process dataset: {e}")
        sys.exit(1)
    
    # Skill requirement: Report null count and which rows
    print(f"Skill load_dataset: Identified {len(null_rows_detected)} deliberate null rows.")
    for report in null_rows_detected:
        print(f" - {report['period']} · {report['ward']} · {report['category']}: {report['reason']}")
        
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Skill: compute_growth
    Takes filtered data and calculates growth metrics while strictly enforcing 
    non-aggregation and formula transparency.
    """
    # Enforcement Rule 1: Never aggregate across wards or categories - Refuse if asked
    aggregation_keywords = ["all", "any", "total", "*"]
    if ward.lower() in aggregation_keywords or category.lower() in aggregation_keywords:
        print(f"REJECTION: Aggregation across {ward}/{category} is forbidden. Refusing to compute.")
        sys.exit(1)

    # Filter for the specific ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered:
        print(f"Skill compute_growth: No data matching Ward: '{ward}' and Category: '{category}'.")
        return []
        
    # Ensure chronology for correct growth calculation
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        curr_period = row['period']
        curr_spend_str = (row.get('actual_spend') or "").strip()
        
        calculated_growth = "n/a"
        formula_used = "n/a"
        
        # Determine value (floating point)
        curr_val = None
        if curr_spend_str:
            try:
                curr_val = float(curr_spend_str)
            except ValueError:
                pass

        # MoM Calculation
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_spend_str = (prev_row.get('actual_spend') or "").strip()
                
                if not curr_spend_str or not prev_spend_str:
                    # Enforcement Rule 2: Flag null row before computing
                    calculated_growth = "NULL"
                    formula_used = f"Calculation skipped: {'Current' if not curr_spend_str else 'Previous'} value is NULL"
                else:
                    prev_val = float(prev_spend_str)
                    if prev_val == 0:
                        calculated_growth = "Inf"
                        formula_used = f"({curr_val} - 0.0) / 0.0"
                    else:
                        growth = (curr_val - prev_val) / prev_val
                        calculated_growth = f"{growth:+.1%}"
                        # Enforcement Rule 3: Show formula used
                        formula_used = f"({curr_val} - {prev_val}) / {prev_val}"
            else:
                formula_used = "Baseline period (No previous month)"
        
        # YoY Calculation
        elif growth_type == "YoY":
            curr_date = datetime.strptime(curr_period, "%Y-%m")
            target_period = f"{curr_date.year - 1}-{curr_date.month:02d}"
            prev_row = next((r for r in filtered if r['period'] == target_period), None)
            
            if not prev_row:
                formula_used = f"No historical data for {target_period}"
            else:
                prev_spend_str = (prev_row.get('actual_spend') or "").strip()
                if not curr_spend_str or not prev_spend_str:
                    calculated_growth = "NULL"
                    formula_used = f"Calculation skipped: {'Current' if not curr_spend_str else 'Previous'} value is NULL"
                else:
                    prev_val = float(prev_spend_str)
                    growth = (curr_val - prev_val) / prev_val
                    calculated_growth = f"{growth:+.1%}"
                    formula_used = f"({curr_val} - {prev_val}) / {prev_val}"
        
        results.append({
            "period": curr_period,
            "ward": ward,
            "category": category,
            "actual_spend": curr_spend_str if curr_spend_str else "NULL",
            "growth_type": growth_type,
            "growth_value": calculated_growth,
            "formula": formula_used,
            "notes": row.get('notes') if not curr_spend_str else ""
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analysis Application")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="Calculation type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output growth CSV")
    
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if --growth-type not specified
    if not args.growth_type:
        print("REJECTION: --growth-type is mandatory (MoM or YoY). System refuse to guess formula.")
        sys.exit(1)
    
    if args.growth_type not in ["MoM", "YoY"]:
        print(f"Error: Unsupported growth-type '{args.growth_type}'. Use MoM or YoY.")
        sys.exit(1)

    # 1. Load and Validate Dataset
    dataset = load_dataset(args.input)
    
    # 2. Compute Growth (with Enforcement Checks)
    output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if not output_rows:
        print("No output generated due to lack of matching data.")
        return

    # 3. Produce Required Output File
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth_value", "formula", "notes"]
    
    try:
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        print(f"Success. Per-ward per-category table saved to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
