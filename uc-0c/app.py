"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

class RefusalError(Exception):
    pass

def load_dataset(file_path: str) -> list:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget file not found: {file_path}")
        
    rows = []
    null_count = 0
    null_rows = []
    
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")
                
        for line_num, row in enumerate(reader, start=2):
            actual_spend_str = row["actual_spend"].strip()
            
            # Check for null values
            if actual_spend_str == "":
                null_count += 1
                null_rows.append((line_num, row["period"], row["ward"], row["category"], row["notes"]))
                actual_spend = None
            else:
                try:
                    actual_spend = float(actual_spend_str)
                except ValueError:
                    null_count += 1
                    null_rows.append((line_num, row["period"], row["ward"], row["category"], "Invalid float value"))
                    actual_spend = None
                    
            budgeted_amount = float(row["budgeted_amount"]) if row["budgeted_amount"] != "" else 0.0
            
            rows.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "budgeted_amount": budgeted_amount,
                "actual_spend": actual_spend,
                "notes": row["notes"]
            })
            
    print(f"Dataset loaded. Total rows: {len(rows)}, Null rows found: {null_count}")
    for nr in null_rows:
        print(f"  Line {nr[0]} | Period: {nr[1]} | Ward: {nr[2]} | Category: {nr[3]} | Reason: {nr[4]}")
        
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses if ward or category are not specified, or if they request aggregation.
    """
    if not growth_type:
        raise RefusalError("Growth type is not specified. Please specify --growth-type (e.g. MoM).")
        
    if growth_type.upper() != "MOM":
        raise RefusalError(f"Unsupported growth-type '{growth_type}'. Only 'MoM' is supported with the available dataset.")
        
    if not ward or ward.lower() in ["all", "total", "any", "aggregate"]:
        raise RefusalError("Aggregation across wards is prohibited. Please specify a single, specific ward.")
        
    if not category or category.lower() in ["all", "total", "any", "aggregate"]:
        raise RefusalError("Aggregation across categories is prohibited. Please specify a single, specific category.")
        
    # Filter rows
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise RefusalError(f"No records found for ward '{ward}' and category '{category}'.")
        
    # Sort chronologically by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        growth = "n/a"
        formula = "n/a"
        
        # Check if current is NULL
        if actual_spend is None:
            growth = "NULL"
            formula = "n/a"
            notes = row["notes"] if row["notes"] else "Actual spend is null"
        elif i == 0:
            # First month
            growth = "n/a"
            formula = "n/a"
        else:
            prev_row = filtered[i-1]
            prev_spend = prev_row["actual_spend"]
            
            if prev_spend is None:
                growth = "NULL"
                formula = "n/a"
                notes = f"Cannot compute growth: previous month's ({prev_row['period']}) actual spend was null."
            else:
                diff = actual_spend - prev_spend
                growth_val = (diff / prev_spend) * 100
                sign = "+" if growth_val >= 0 else ""
                growth = f"{sign}{growth_val:.1f}%"
                formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                
        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL" if actual_spend is None else actual_spend,
            "growth": growth,
            "formula": formula,
            "notes": notes
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Specific ward name")
    parser.add_argument("--category", required=False, help="Specific category name")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    
    args = parser.parse_args()
    
    try:
        # Check constraints before loading
        if not args.growth_type:
            raise RefusalError("Refusal: --growth-type is not specified. You must choose MoM.")
            
        if not args.ward or args.ward.lower() in ["all", "total", "any", "aggregate"]:
            raise RefusalError("Refusal: Aggregation across wards is not permitted. Please specify a single ward.")
            
        if not args.category or args.category.lower() in ["all", "total", "any", "aggregate"]:
            raise RefusalError("Refusal: Aggregation across categories is not permitted. Please specify a single category.")
            
        rows = load_dataset(args.input)
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Write output file
        with open(args.output, mode="w", newline="", encoding="utf-8") as outfile:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
        print(f"Growth calculation succeeded. Output written to {args.output}")
        
    except RefusalError as re_err:
        print(f"Refusal: {str(re_err)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
