"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> list:
    """
    Role: Skill 1 - Data Loader.
    Intent: Read CSV, validate columns, and report nulls.
    Context: budget CSV file.
    Enforcement: Proactively reports null rows and their reasons.
    """
    data = []
    null_rows = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2): # Header is line 1
                if not row['actual_spend'].strip():
                    null_rows.append((i, row['period'], row['ward'], row['category'], row['notes']))
                data.append(row)
                
        if null_rows:
            print(f"REPORT: Found {len(null_rows)} rows with null actual_spend:")
            for line, period, ward, cat, note in null_rows:
                print(f"  - Line {line}: {period} | {ward} | {cat} | Reason: {note}")
        else:
            print("REPORT: No null actual_spend values found.")
            
        return data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required column {e}")
        sys.exit(1)

def compute_growth(ward: str, category: str, growth_type: str, data: list) -> list:
    """
    Role: Skill 2 - Growth Calculator.
    Intent: Calculate MoM/YoY growth with formula transparency.
    Context: Filtered budget data.
    Enforcement: Flags nulls and shows calculation formula.
    """
    # Enforcement: Filter strictly by ward and category (no aggregation allowed)
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual = row['actual_spend']
        note = row['notes']
        
        result_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual if actual else "NULL",
            "Growth": "n/a",
            "Formula": "n/a"
        }
        
        # Enforcement: Null Handling
        if not actual:
            result_row["Growth"] = "NULL (Flagged)"
            result_row["Formula"] = f"Calculation skipped: {note}"
            results.append(result_row)
            continue
            
        now_val = float(actual)
        
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_val_str = prev_row['actual_spend']
                
                if prev_val_str:
                    prev_val = float(prev_val_str)
                    growth = ((now_val - prev_val) / prev_val) * 100
                    result_row["Growth"] = f"{growth:+.1f}%"
                    result_row["Formula"] = f"({now_val} - {prev_val}) / {prev_val}"
                else:
                    result_row["Growth"] = "n/a"
                    result_row["Formula"] = "Previous month was NULL"
            else:
                result_row["Formula"] = "First month in sequence"
        
        # Note: YoY not implemented as per README focus on MoM examples, 
        # but the structure allows for it.
        
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact string)")
    parser.add_argument("--category", required=True, help="Category name (exact string)")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    # Enforcement: Input Validation
    if not args.growth_type:
        print("REFUSAL: --growth-type (MoM or YoY) is mandatory. Please specify.")
        return

    print(f"Analyzing {args.ward} | {args.category} | {args.growth_type}...")

    # Step 1: Load
    data = load_dataset(args.input)

    # Step 2: Compute
    results = compute_growth(args.ward, args.category, args.growth_type, data)

    # Step 3: Write Output
    if results:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "Growth", "Formula"]
        try:
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Results written to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()
