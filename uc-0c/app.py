"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """Reads a budget CSV file, validates columns, and reports nulls."""
    dataset = []
    null_count = 0
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2): # 1 is header
            dataset.append(row)
            if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                null_count += 1
                null_rows.append(f"Row {row_num}: Ward {row.get('ward')}, Category {row.get('category')}, Period {row.get('period')}. Note: {row.get('notes')}")
                
    if null_count > 0:
        print(f"--- DATASET LOAD REPORT ---")
        print(f"Found {null_count} rows with NULL actual_spend:")
        for r in null_rows:
            print(f"  - {r}")
        print(f"---------------------------\n")
        
    return dataset

def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """Computes growth, enforcing rules on aggregation and formula display."""
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        raise ValueError("ENFORCEMENT REFUSAL: Never aggregate data across wards or categories unless explicitly instructed.")
        
    if not growth_type:
        raise ValueError("ENFORCEMENT REFUSAL: --growth-type not specified. Never guess the formula.")
        
    if growth_type.lower() != "mom":
        raise ValueError(f"ENFORCEMENT REFUSAL: Unsupported growth type '{growth_type}'. Cannot assume formula.")

    # Filter data
    filtered = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row["period"]
        spend_str = row["actual_spend"].strip() if row.get("actual_spend") else ""
        notes = row.get("notes", "").strip()
        
        if spend_str == "":
            actual_spend_val = "NULL"
            growth_val = f"FLAGGED: {notes} - not computed"
            prev_spend = None # Break the chain for next MoM calculation
        else:
            actual_spend_val = float(spend_str)
            if prev_spend is None:
                growth_val = "n/a (no previous period)"
            else:
                growth_pct = ((actual_spend_val - prev_spend) / prev_spend) * 100
                sign = "+" if growth_pct > 0 else ""
                growth_val = f"{sign}{growth_pct:.1f}% (Formula: ({actual_spend_val} - {prev_spend}) / {prev_spend})"
            
            prev_spend = actual_spend_val
            
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_spend_val,
            "MoM Growth": growth_val
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    parser.add_argument("--ward", help="Target ward")
    parser.add_argument("--category", help="Target category")
    parser.add_argument("--growth-type", help="Growth metric to calculate (e.g., MoM)")
    
    args = parser.parse_args()
    
    try:
        dataset = load_dataset(args.input)
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Success. Growth output written to {args.output}")
        
    except ValueError as e:
        print(f"\n[SYSTEM REFUSAL] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
