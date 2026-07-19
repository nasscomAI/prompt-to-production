"""
UC-0C app.py — Calculate growth rates and handle null values cleanly.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import os

def load_dataset(file_path: str) -> list:
    """
    Reads the ward budget CSV file, validates the columns, and checks for and logs any null actual_spend rows.
    Returns: list of dicts representing the rows in the CSV.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")
        
    rows = []
    null_rows = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2): # Header is line 1
            actual_spend_str = row.get("actual_spend", "").strip()
            if not actual_spend_str:
                null_rows.append((line_no, row.get("period"), row.get("ward"), row.get("category"), row.get("notes")))
            rows.append(row)
            
    print(f"Loaded {len(rows)} rows from dataset.")
    print(f"Found {len(null_rows)} null actual_spend rows in the input dataset:")
    for line, period, ward, cat, notes in null_rows:
        print(f"  Line {line}: Period: {period} | Ward: {ward} | Category: {cat} | Reason: {notes}")
        
    return rows


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters the dataset to the specified ward and category, sorts by period, and calculates period-over-period growth with formulas.
    Returns: list of dicts containing the computed growth rates, formula strings, and notes for each period.
    """
    # Filter rows by ward and category
    filtered = []
    for row in dataset:
        if row.get("ward") == ward and row.get("category") == category:
            filtered.append(row)
            
    if not filtered:
        print(f"Warning: No rows found matching ward '{ward}' and category '{category}'.")
        return []
        
    # Sort by period YYYY-MM
    filtered.sort(key=lambda x: x.get("period", ""))
    
    results = []
    for i, row in enumerate(filtered):
        period = row.get("period")
        budgeted = float(row.get("budgeted_amount", 0.0))
        notes = row.get("notes", "").strip()
        
        # Check actual spend of current row
        actual_str = row.get("actual_spend", "").strip()
        if not actual_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": "n/a",
                "notes": notes if notes else "Actual spend is missing"
            })
            continue
            
        try:
            curr_spend = float(actual_str)
        except ValueError:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": "INVALID",
                "growth": "NULL",
                "formula": "n/a",
                "notes": f"Invalid float value: {actual_str}"
            })
            continue
        
        if i == 0:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": curr_spend,
                "growth": "NULL",
                "formula": "n/a",
                "notes": "First period in dataset"
            })
            continue
            
        # Check previous row actual spend
        prev_row = filtered[i-1]
        prev_actual_str = prev_row.get("actual_spend", "").strip()
        if not prev_actual_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": curr_spend,
                "growth": "NULL",
                "formula": "n/a",
                "notes": f"Previous month ({prev_row.get('period')}) spend was NULL"
            })
            continue
            
        try:
            prev_spend = float(prev_actual_str)
        except ValueError:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": budgeted,
                "actual_spend": curr_spend,
                "growth": "NULL",
                "formula": "n/a",
                "notes": f"Previous month ({prev_row.get('period')}) spend was invalid: {prev_actual_str}"
            })
            continue
        
        # Compute growth percentage
        if prev_spend == 0:
            growth_pct = 0.0
            growth_str = "0.0%"
            formula_str = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
        else:
            diff = curr_spend - prev_spend
            growth_pct = (diff / prev_spend) * 100.0
            
            if growth_pct > 0:
                growth_str = f"+{growth_pct:.1f}%"
            elif growth_pct < 0:
                # Use unicode minus sign − (U+2212)
                growth_str = f"−{abs(growth_pct):.1f}%"
            else:
                growth_str = "0.0%"
                
            formula_str = f"({curr_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
            
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": curr_spend,
            "growth": growth_str,
            "formula": formula_str,
            "notes": notes
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Name of the ward")
    parser.add_argument("--category", help="Name of the category")
    parser.add_argument("--growth-type", dest="growth_type", help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # ENFORCEMENT 4: If growth-type not specified - refuse and ask, never guess
    if not args.growth_type:
        print("Error: --growth-type must be explicitly specified (e.g., MoM). Defaulting or guessing is not permitted.")
        exit(1)
        
    if args.growth_type.lower() != "mom":
        print(f"Error: Unsupported growth type '{args.growth_type}'. Only 'MoM' is supported.")
        exit(1)
        
    # ENFORCEMENT 1: Never aggregate across wards or categories - refuse if asked
    if not args.ward or args.ward.strip().lower() in ["all", "any", "aggregated", "total"]:
        print("Error: A specific ward must be provided. All-ward or aggregated calculations are strictly prohibited.")
        exit(1)
        
    if not args.category or args.category.strip().lower() in ["all", "any", "aggregated", "total"]:
        print("Error: A specific category must be provided. All-category or aggregated calculations are strictly prohibited.")
        exit(1)
        
    try:
        dataset = load_dataset(args.input)
        
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        # Write output to CSV
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"])
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully calculated growth and wrote to {args.output}")
    except Exception as e:
        print(f"Error during calculation process: {e}")
        exit(1)


if __name__ == "__main__":
    main()
