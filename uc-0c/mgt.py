import csv
import argparse
import sys
import os

def load_dataset(file_path):
    """
    Reads the CSV, validates columns, and reports missing mandatory data per row.
    Rule 2: Null-Transparency - explicitly list deliberate nulls by Ward/Category/Period and show reason.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    records = []
    null_records_report = []
    
    # Mandatory columns for data integrity checks
    mandatory_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend']
    # All required columns including notes for reporting
    required_cols = mandatory_cols + ['notes']

    try:
        # utf-8-sig handles BOM characters automatically
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            # Basic Column Validation
            if not all(col in (reader.fieldnames or []) for col in required_cols):
                print("Error: Missing required columns in dataset.")
                sys.exit(1)

            for row_num, row in enumerate(reader, start=2): # Row 1 is header
                missing_in_row = []
                for col in mandatory_cols:
                    val = (row.get(col) or "").strip().lower()
                    if val in ["", "null", "na"]:
                        missing_in_row.append(col)
                
                if missing_in_row:
                    # Satisfying Rule 2 & skills.md exact requirement
                    period = row.get('period', 'Unknown')
                    ward = row.get('ward', 'Unknown')
                    category = row.get('category', 'Unknown')
                    notes = row.get('notes', 'No reason specified')
                    null_records_report.append(f"- {period} | {ward} | {category} | Reason: {notes}")
                
                records.append(row)

        # Print the fully compliant validation report
        print(f"Validation Report: {len(null_records_report)} deliberate null rows identified.")
        for report in null_records_report:
            print(report)
            
        return records

    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

def compute_growth(data, target_ward, target_category, growth_type):
    """
    Engine for growth calculation with prioritized logic (Rules 1, 2, 3).
    """
    # Rule 1: Anti-Aggregation Rule
    if target_ward.lower() in ["all", "any"] or target_category.lower() in ["all", "any"]:
        print("Error: Anti-Aggregation Rule violation. You must specify a specific Ward")
        sys.exit(1)

    # Filter data for target ward and category
    subset = [r for r in data if r.get('ward') == target_ward and r.get('category') == target_category]
    # Sort by period to ensure MoM/YoY order is strictly chronological
    subset.sort(key=lambda x: x.get('period', ''))

    results = []
    offset = 1 if growth_type == 'MoM' else 12

    for i, current in enumerate(subset):
        curr_spend_s = (current.get('actual_spend') or "").strip()
        curr_budget_s = (current.get('budgeted_amount') or "").strip()
        
        row_res = {
            "Period": current.get('period', 'N/A'),
            "Spend": curr_spend_s if curr_spend_s and curr_spend_s.lower() not in ["null", "na"] else "NULL"
        }

        # PRIORITY 1: Rule 2 Null Transparency (Current Row)
        if not curr_spend_s or curr_spend_s.lower() in ["null", "na"] or \
           not curr_budget_s or curr_budget_s.lower() in ["null", "na"]:
            row_res["Growth"] = "NULL"
            row_res["Formula"] = f"NULL - Data missing due to {current.get('notes', 'No reason specified')}"
            
        # PRIORITY 2: Baseline Handling (Rule 3)
        elif i < offset:
            row_res["Growth"] = "N/A"
            row_res["Formula"] = "N/A"
            
        # PRIORITY 3: Edge Cases & Math
        else:
            previous = subset[i - offset]
            prev_spend_s = (previous.get('actual_spend') or "").strip()
            
            # Sub-Priority: Null Baseline (if previous month was null)
            if not prev_spend_s or prev_spend_s.lower() in ["null", "na"]:
                curr_v = float(curr_spend_s)
                row_res["Growth"] = "NULL"
                row_res["Formula"] = f"({curr_v:.1f} - NULL) / NULL"
            else:
                curr_v = float(curr_spend_s)
                prev_v = float(prev_spend_s)
                
                # Sub-Priority: Division by Zero safeguard
                if prev_v == 0:
                    row_res["Growth"] = "N/A"
                    row_res["Formula"] = f"({curr_v:.1f} - 0.0) / 0.0 (Div by Zero)"
                else:
                    growth_val = (curr_v - prev_v) / prev_v
                    # Rule 3: Formula Visibility & Precise Formatting
                    row_res["Growth"] = f"{growth_val:+.1%}"
                    row_res["Formula"] = f"({curr_v:.1f} - {prev_v:.1f}) / {prev_v:.1f}"
                    
        results.append(row_res)
    
    return results

def main():
    # Orchestration: Arguments setup
    parser = argparse.ArgumentParser(description="Municipal Spending Growth Analysis Tool")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=True, help="Target Ward name")
    parser.add_argument("--category", required=True, help="Target Category name")
    parser.add_argument("--growth-type", choices=['MoM', 'YoY'], help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Output CSV path")
    
    args = parser.parse_args()

    # Rule 4: Manual No-Guessing Rule Implementation
    if args.growth_type is None:
        print("Error: --growth-type (MoM or YoY) must be specified. I will not guess")
        sys.exit(1)

    # Execute Pipeline
    data = load_dataset(args.input)
    analysis = compute_growth(data, args.ward, args.category, args.growth_type)

    # Output Persistence
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            headers = ["Period", "Spend", "Growth", "Formula"]
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(analysis)
        print(f"Success: Final processed dataset written to {args.output}")
    except Exception as e:
        print(f"Error writing to output: {e}")

if __name__ == "__main__":
    main()