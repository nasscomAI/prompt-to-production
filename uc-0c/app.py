"""
UC-0C app.py — Number That Looks Right.
Implements the skills load_dataset and compute_growth.
Strictly adheres to enforcement rules in agents.md.
"""
import argparse
import csv
import os
import sys

def normalize_dash(s: str) -> str:
    """Helper to normalize different dash/minus characters to standard hyphen."""
    if not s:
        return ""
    return s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-").strip()

def load_dataset(file_path: str) -> list:
    """
    Reads the input CSV budget file, validates that all required columns
    (period, ward, category, budgeted_amount, actual_spend, notes) are present,
    and identifies and logs the counts and row details of any null actual spend records.
    """
    if not os.path.exists(file_path):
        error_msg = f"FileNotFoundError: The file '{file_path}' does not exist."
        print(error_msg, file=sys.stderr)
        raise FileNotFoundError(error_msg)

    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = set(reader.fieldnames or [])
            
            # Check required columns
            missing = required_columns - headers
            if missing:
                error_msg = f"ValueError: Missing required columns in dataset: {', '.join(missing)}"
                print(error_msg, file=sys.stderr)
                raise ValueError(error_msg)
                
            for row in reader:
                rows.append(row)
    except Exception as e:
        if not isinstance(e, (FileNotFoundError, ValueError)):
            print(f"Error reading file '{file_path}': {str(e)}", file=sys.stderr)
        raise

    # Identify and report null actual spend records to stderr
    null_rows = []
    for idx, r in enumerate(rows, start=2):  # Header is line 1, data starts at line 2
        actual = r["actual_spend"].strip()
        if not actual:
            null_rows.append((idx, r))

    print(f"Successfully loaded {len(rows)} rows from dataset.", file=sys.stderr)
    print(f"Total null actual_spend rows detected: {len(null_rows)}", file=sys.stderr)
    for line_no, r in null_rows:
        print(f"  [NULL ROW] Line {line_no}: Period={r['period']}, Ward='{r['ward']}', Category='{r['category']}'", file=sys.stderr)
        print(f"             Reason/Notes: '{r['notes']}'", file=sys.stderr)

    return rows

def compute_growth(rows: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """
    Calculates period-over-period growth (such as MoM growth) for a specific ward and category combination,
    generating a per-period table with explicit formulas shown for each non-null row and flagging null spend values.
    Refuses execution if parameters are missing, invalid, or imply aggregation.
    """
    # Refusal Check: Growth type must be specified
    if not growth_type:
        print("Refusal Error: Growth type parameter (--growth-type) was not specified. Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    if growth_type.upper() != "MOM":
        print(f"Refusal Error: Unsupported growth type '{growth_type}'. Only 'MoM' is supported.", file=sys.stderr)
        sys.exit(1)

    # Refusal Check: Missing target ward/category
    if not target_ward or not target_category:
        print("Refusal Error: Both --ward and --category must be specified. Refusing to proceed.", file=sys.stderr)
        sys.exit(1)

    # Refusal Check: Aggregation requested
    if target_ward.strip().lower() == "any" or target_category.strip().lower() == "any":
        print("Refusal Error: All-ward or All-category aggregation requested. System must REFUSE.", file=sys.stderr)
        sys.exit(1)

    # Filter rows based on normalized ward and category names to handle different dash formats
    norm_target_ward = normalize_dash(target_ward)
    norm_target_category = normalize_dash(target_category)

    # Gather matching rows
    matched_rows = []
    for r in rows:
        if normalize_dash(r["ward"]) == norm_target_ward and normalize_dash(r["category"]) == norm_target_category:
            matched_rows.append(r)

    if not matched_rows:
        print(f"Refusal Error: No matching data found for Ward='{target_ward}' and Category='{target_category}'. Refusing execution.", file=sys.stderr)
        sys.exit(1)

    # Sort chronologically by period
    matched_rows.sort(key=lambda x: x["period"])

    results = []
    for idx, current_row in enumerate(matched_rows):
        period = current_row["period"]
        actual_str = current_row["actual_spend"].strip()
        ward_display = current_row["ward"]
        category_display = current_row["category"]

        # 1. Check if current month actual spend is null
        if not actual_str:
            print(f"Flagged null actual spend row: Period={period}, Ward='{ward_display}', Category='{category_display}'. Reason: {current_row['notes']}", file=sys.stderr)
            results.append({
                "Ward": ward_display,
                "Category": category_display,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "MoM Growth": "NULL",
                "Formula": "n/a",
                "Notes": current_row["notes"] or "Data missing"
            })
            continue

        current_val = float(actual_str)

        # 2. First period (no previous period in subset)
        if idx == 0:
            results.append({
                "Ward": ward_display,
                "Category": category_display,
                "Period": period,
                "Actual Spend (₹ lakh)": f"{current_val:.1f}",
                "MoM Growth": "n/a",
                "Formula": "n/a",
                "Notes": current_row["notes"] or "First month of data"
            })
            continue

        # 3. Check previous period actual spend
        prev_row = matched_rows[idx - 1]
        prev_actual_str = prev_row["actual_spend"].strip()

        if not prev_actual_str:
            # Previous month was null, cannot compute growth
            results.append({
                "Ward": ward_display,
                "Category": category_display,
                "Period": period,
                "Actual Spend (₹ lakh)": f"{current_val:.1f}",
                "MoM Growth": "NULL",
                "Formula": "n/a",
                "Notes": f"Not computed: Previous month ({prev_row['period']}) spend was NULL ({prev_row['notes']})"
            })
            continue

        prev_val = float(prev_actual_str)

        # 4. Perform calculation
        if prev_val == 0.0:
            growth_str = "n/a"
            formula_str = f"({current_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}"
            note_str = "Division by zero"
        else:
            growth_val = (current_val - prev_val) / prev_val
            # Use unicode minus sign (U+2212) for negative numbers as shown in README reference values
            if growth_val > 0:
                growth_str = f"+{growth_val:.1%}"
            elif growth_val < 0:
                growth_str = f"\u2212{abs(growth_val):.1%}"
            else:
                growth_str = "0.0%"
            formula_str = f"({current_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}"
            note_str = current_row["notes"]

        results.append({
            "Ward": ward_display,
            "Category": category_display,
            "Period": period,
            "Actual Spend (₹ lakh)": f"{current_val:.1f}",
            "MoM Growth": growth_str,
            "Formula": formula_str,
            "Notes": note_str
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget growth calculator")
    parser.add_argument("--input", help="Path to the input budget CSV file")
    parser.add_argument("--ward", help="Name of the ward (or 'Any' to test refusal)")
    parser.add_argument("--category", help="Name of the budget category (or 'Any' to test refusal)")
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g. MoM)")
    parser.add_argument("--output", help="Path to write the resulting CSV growth table")
    
    args = parser.parse_args()

    # If --growth-type is not specified at all, check it and refuse
    if not args.growth_type:
        print("Refusal Error: Growth type parameter (--growth-type) is not specified. Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    if not args.input:
        print("Error: --input parameter is required.", file=sys.stderr)
        sys.exit(1)
        
    if not args.output:
        print("Error: --output parameter is required.", file=sys.stderr)
        sys.exit(1)

    try:
        # Load and validate
        rows = load_dataset(args.input)
        
        # Compute growth
        results = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        # Ensure output directory exists
        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        # Write results
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            else:
                f.write("")
                
        print(f"Growth calculation table successfully written to: {args.output}", file=sys.stderr)
        
    except Exception as e:
        print(f"Execution failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
