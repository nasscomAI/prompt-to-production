"""
UC-0C app.py — CMC Ward Budget Growth Calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import sys
import os
import csv

def load_dataset(file_path: str) -> list:
    """
    Reads the budget CSV file, validates its columns, and reports any rows containing null actual spend values.
    """
    if not os.path.exists(file_path):
        sys.stderr.write(f"Error: Budget file '{file_path}' does not exist.\n")
        sys.exit(1)
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to read budget file '{file_path}'. Details: {e}\n")
        sys.exit(1)
        
    required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_cols:
        if col not in fieldnames:
            sys.stderr.write(f"Error: Input CSV is missing required column '{col}'.\n")
            sys.exit(1)
            
    # Count null actual spend rows and print warning to stderr
    null_rows = []
    for idx, row in enumerate(rows):
        val = row.get("actual_spend", "").strip()
        if not val:
            null_rows.append(f"Row {idx+2}: Period {row['period']}, Ward {row['ward']}, Category {row['category']} (Reason: {row['notes']})")
            
    if null_rows:
        sys.stderr.write(f"Found {len(null_rows)} rows with null actual_spend:\n")
        for nr in null_rows:
            sys.stderr.write(f"  - {nr}\n")
            
    return rows

def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM growth for a specific ward and category, returning a per-period table with formulas and flagged nulls.
    """
    # Validation against aggregation or missing values
    if not ward or not category or not growth_type:
        sys.stderr.write("Error: Ward, category, and growth-type must all be specified. Aggregation is not permitted.\n")
        sys.exit(1)
        
    if ward.lower() == "any" or category.lower() == "any" or ward.lower() == "all" or category.lower() == "all":
        sys.stderr.write("Error: Refusing to aggregate across multiple wards or categories.\n")
        sys.exit(1)
        
    if growth_type != "MoM":
        sys.stderr.write(f"Error: Unsupported growth-type '{growth_type}'. Only 'MoM' is supported.\n")
        sys.exit(1)
        
    # Filter records
    filtered = [r for r in records if r["ward"] == ward and r["category"] == category]
    
    if not filtered:
        sys.stderr.write(f"Error: No records found for Ward '{ward}' and Category '{category}'.\n")
        sys.exit(1)
        
    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    result_table = []
    
    for i, row in enumerate(filtered):
        curr_period = row["period"]
        curr_spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        # Convert budgeted_amount
        try:
            budgeted_amount = float(row["budgeted_amount"])
        except ValueError:
            budgeted_amount = 0.0
            
        # Determine actual spend float or None
        if not curr_spend_str:
            curr_spend = None
        else:
            try:
                curr_spend = float(curr_spend_str)
            except ValueError:
                curr_spend = None
                
        # For MoM growth, we look at the previous row in the sorted list
        if i == 0:
            growth = "n/a"
            formula = "n/a"
        else:
            prev_row = filtered[i-1]
            prev_spend_str = prev_row["actual_spend"].strip()
            
            if not prev_spend_str:
                prev_spend = None
            else:
                try:
                    prev_spend = float(prev_spend_str)
                except ValueError:
                    prev_spend = None
                    
            if curr_spend is None:
                growth = "NULL"
                formula = "n/a"
            elif prev_spend is None:
                # If previous spend was NULL, we can't calculate growth
                growth = "NULL"
                formula = f"({curr_spend} - NULL) / NULL"
            else:
                # Calculate growth percentage
                if prev_spend == 0:
                    growth_pct = 0.0
                else:
                    growth_pct = ((curr_spend - prev_spend) / prev_spend) * 100
                    
                sign = "+" if growth_pct >= 0 else ""
                growth_str = f"{sign}{growth_pct:.1f}%"
                
                # Check for note on current row to append
                if notes:
                    growth = f"{growth_str} ({notes})"
                else:
                    growth = growth_str
                    
                formula = f"({curr_spend} - {prev_spend}) / {prev_spend}"
                
        result_table.append({
            "period": curr_period,
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": row["actual_spend"],
            "notes": row["notes"],
            "growth": growth,
            "formula": formula
        })
        
    return result_table

def main():
    parser = argparse.ArgumentParser(description="CMC Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, help="Growth type (only MoM supported)")
    parser.add_argument("--output", required=True, help="Path to write the results CSV")
    
    args = parser.parse_args()
    
    # Load
    records = load_dataset(args.input)
    
    # Compute
    growth_table = compute_growth(records, args.ward, args.category, args.growth-type if hasattr(args, 'growth-type') else args.growth_type)
    
    # Write to output CSV
    try:
        out_dir = os.path.dirname(args.output)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes", "growth", "formula"]
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(growth_table)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to write output file '{args.output}'. Details: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
