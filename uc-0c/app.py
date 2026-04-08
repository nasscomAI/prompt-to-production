"""
UC-0C app.py — Budget Growth Calculator.
Implements RICE framework and CRAFT loop to calculate MoM growth.
Handles null actual_spend rows and prevents unauthorized aggregation.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path):
    """Skill 1: Reads CSV, validates columns, and reports null counts."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    data = []
    null_count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Schema validation
            required_cols = ['period', 'ward', 'category', 'actual_spend', 'notes']
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"Error: CSV schema mismatch. Expected: {required_cols}")
                sys.exit(1)
                
            for row in reader:
                # Identification of null rows (Enforcement Rule 2)
                if not row['actual_spend'] or row['actual_spend'].strip() == "":
                    null_count += 1
                data.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
            
    print(f"Successfully loaded {len(data)} rows. Found {null_count} null rows.")
    return data

def normalize_string(s):
    """Helper to handle hyphen/en-dash mismatches between terminal and data."""
    return s.replace('–', '-').replace('—', '-').strip().lower()

def compute_growth(data, target_ward, target_cat, growth_type):
    """Skill 2: Calculates growth table with formula auditing and null flagging."""
    # Normalized filtering to prevent "No data found" due to en-dash/hyphen mismatch
    norm_ward = normalize_string(target_ward)
    norm_cat = normalize_string(target_cat)
    
    filtered = [
        r for r in data 
        if normalize_string(r['ward']) == norm_ward 
        and normalize_string(r['category']) == norm_cat
    ]
    
    if not filtered:
        print(f"Error: No data found for Ward: '{target_ward}' and Category: '{target_cat}'")
        print("Check for typos or special characters (like en-dashes vs hyphens).")
        sys.exit(1)

    # Sort chronologically (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    # Enforcement Rule 3: Show formula
    formula_str = "[(Current - Previous) / Previous] * 100" if growth_type == "MoM" else "Custom"

    for row in filtered:
        period = row['period']
        notes = row['notes']
        raw_spend = row['actual_spend']
        
        current_spend = None
        if raw_spend and raw_spend.strip() != "":
            try:
                current_spend = float(raw_spend)
            except ValueError:
                current_spend = None

        # Logic for result row
        if current_spend is None:
            # Enforcement Rule 2: Flag nulls and report reason
            growth_val = f"NULL_FLAGGED: {notes}"
        elif prev_spend is None or prev_spend == 0:
            growth_val = "N/A (Baseline)"
        else:
            growth_pct = ((current_spend - prev_spend) / prev_spend) * 100
            growth_val = f"{growth_pct:+.1f}%"
        
        results.append({
            "Period": period,
            "Ward": row['ward'],
            "Category": row['category'],
            "Actual Spend (₹ lakh)": raw_spend if raw_spend else "NULL",
            "MoM Growth": growth_val,
            "Formula Used": formula_str
        })
        prev_spend = current_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name (e.g. Ward 1 – Kasba)")
    parser.add_argument("--category", required=True, help="Budget category")
    parser.add_argument("--growth-type", help="Type of growth calculation (MoM)")
    parser.add_argument("--output", required=True, help="Path to results CSV")
    
    args = parser.parse_args()

    # Enforcement Rule 4: Refuse if growth-type missing
    if not args.growth_type:
        print("Error: --growth-type (e.g., MoM) is required. System refuses to guess.")
        sys.exit(1)

    # Step 1: Load (Control)
    dataset = load_dataset(args.input)
    
    # Step 2: Compute (Run)
    report_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    # Step 3: Write Output (Track)
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=report_rows[0].keys())
            writer.writeheader()
            writer.writerows(report_rows)
        print(f"✅ Growth report generated: {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}")

if __name__ == "__main__":
    main()