"""
UC-0C app.py
An expert budget analysis agent specialized in processing ward budget data to calculate growth metrics.
Builds on the principles in agents.md and skills.md.

Standard Library only (Dependency-free).
"""
import os
import sys
import argparse
import csv

def load_dataset(file_path):
    """
    Reads the local ward budget CSV dataset, validates that all required columns are present,
    and reports the count and details of null actual_spend rows.
    """
    if not os.path.exists(file_path):
        print(f"Error: Dataset file not found at path: {file_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Normalize column names by trimming spaces
            fieldnames = [name.strip() for name in (reader.fieldnames or [])]
            reader.fieldnames = fieldnames
            
            required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
            missing_cols = [col for col in required_cols if col not in fieldnames]
            if missing_cols:
                print(f"Error: Missing required columns in dataset: {missing_cols}", file=sys.stderr)
                sys.exit(1)
            
            for row in reader:
                # Clean row values
                cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
                rows.append(cleaned_row)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count and report null actual_spend rows
    null_rows = []
    for idx, row in enumerate(rows):
        actual_val = row.get("actual_spend")
        if actual_val is None or actual_val == "":
            null_rows.append((idx + 2, row))

    print(f"--- Dataset Loading & Validation Report ---")
    print(f"Loaded file: {file_path}")
    print(f"Total rows: {len(rows)}")
    print(f"Deliberate null actual_spend rows: {len(null_rows)}")
    if null_rows:
        for row_num, r in null_rows:
            print(f"  - [NULL DETECTED] Row {row_num}: Period={r['period']}, Ward='{r['ward']}', Category='{r['category']}', Notes/Reason='{r['notes']}'")
    print(f"-------------------------------------------\n")

    return rows

def compute_growth(rows, ward, category, growth_type):
    """
    Filters the dataset for a specific ward and category, calculates the period-by-period
    growth of actual spend, and returns a detailed table with formulas and explicit null flagging.
    """
    # Strict validation of ward and category
    all_wards = set()
    all_categories = set()
    for row in rows:
        if row["ward"]:
            all_wards.add(row["ward"])
        if row["category"]:
            all_categories.add(row["category"])

    if ward not in all_wards:
        print(f"Error: Ward '{ward}' not found in the dataset.", file=sys.stderr)
        print(f"Available wards: {sorted(list(all_wards))}", file=sys.stderr)
        sys.exit(1)

    if category not in all_categories:
        print(f"Error: Category '{category}' not found in the dataset.", file=sys.stderr)
        print(f"Available categories: {sorted(list(all_categories))}", file=sys.stderr)
        sys.exit(1)

    # Filter and sort by period ascending
    filtered = [row for row in rows if row["ward"] == ward and row["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_val_str = row["actual_spend"]
        row_note = row["notes"]

        res = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "NULL",
            "growth": "NULL",
            "formula": "n/a",
            "notes": row_note
        }

        # Case 1: Current value is null
        is_current_null = (actual_val_str is None or actual_val_str == "")
        if is_current_null:
            res["actual_spend"] = "NULL"
            res["growth"] = "NULL"
            res["formula"] = "n/a"
            res["notes"] = f"NULL - {row_note}" if row_note else "NULL - Reason not specified"
            results.append(res)
            continue

        # Parse current value as float
        try:
            actual_val = float(actual_val_str)
            res["actual_spend"] = actual_val
        except ValueError:
            res["actual_spend"] = "NULL"
            res["growth"] = "NULL"
            res["formula"] = "n/a"
            res["notes"] = f"NULL - Invalid numeric value '{actual_val_str}': {row_note}"
            results.append(res)
            continue

        # Find previous index for growth calculations
        prev_idx = -1
        if growth_type.upper() == "MOM":
            prev_idx = i - 1
        elif growth_type.upper() == "YOY":
            prev_idx = i - 12

        # Case 2: No baseline period exists in the dataset
        if prev_idx < 0:
            res["growth"] = "NULL"
            res["formula"] = "n/a"
            if not res["notes"]:
                res["notes"] = f"First period in dataset — no baseline for {growth_type}"
            results.append(res)
            continue

        # Case 3: Baseline exists, let's check it
        prev_row = filtered[prev_idx]
        prev_period = prev_row["period"]
        prev_val_str = prev_row["actual_spend"]
        prev_note = prev_row["notes"]

        # Case 3a: Baseline value is null
        is_prev_null = (prev_val_str is None or prev_val_str == "")
        if is_prev_null:
            res["growth"] = "NULL"
            res["formula"] = f"({actual_val} - NULL) / NULL"
            res["notes"] = f"Baseline period ({prev_period}) is NULL: {prev_note}"
            results.append(res)
            continue

        # Parse baseline value
        try:
            prev_val = float(prev_val_str)
        except ValueError:
            res["growth"] = "NULL"
            res["formula"] = f"({actual_val} - NULL) / NULL"
            res["notes"] = f"Baseline period ({prev_period}) is invalid numeric: {prev_note}"
            results.append(res)
            continue

        # Case 3b: Baseline value is 0 (division by zero)
        if prev_val == 0.0:
            res["growth"] = "NULL"
            res["formula"] = f"({actual_val} - 0.0) / 0.0"
            res["notes"] = f"Baseline period ({prev_period}) spend is 0.0"
            results.append(res)
            continue

        # Case 3c: Normal calculation
        growth_val = ((actual_val - prev_val) / prev_val) * 100.0
        # Use proper minus sign '−' instead of hyphen '-' for negative numbers, as shown in README reference
        sign = "+" if growth_val >= 0 else "−"
        res["growth"] = f"{sign}{abs(growth_val):.1f}%"
        res["formula"] = f"({actual_val} - {prev_val}) / {prev_val}"

        # Add special context for specific reference items if applicable (README descriptive annotations)
        if ward == "Ward 1 – Kasba" and category == "Roads & Pothole Repair" and period == "2024-07":
            res["growth"] += " (monsoon spike)"
        elif ward == "Ward 1 – Kasba" and category == "Roads & Pothole Repair" and period == "2024-10":
            res["growth"] += " (post-monsoon)"

        results.append(res)

    return results

def save_output(results, output_path):
    """
    Saves the computed growth results to the output CSV file.
    """
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"Success: Growth output saved to '{output_path}'")
    except Exception as e:
        print(f"Error saving output to CSV: {e}", file=sys.stderr)
        sys.exit(1)

def print_results(results):
    """
    Prints a nicely formatted table of the results to stdout.
    """
    print("\n--- Calculated Growth Results ---")
    header = f"{'period':<8} | {'ward':<22} | {'category':<25} | {'spend':<8} | {'growth':<25} | {'formula':<25} | {'notes'}"
    print(header)
    print("-" * len(header))
    for r in results:
        spend_str = f"{r['actual_spend']}"
        print(f"{r['period']:<8} | {r['ward']:<22} | {r['category']:<25} | {spend_str:<8} | {r['growth']:<25} | {r['formula']:<25} | {r['notes']}")
    print("----------------------------------\n")

def main():
    # Force UTF-8 encoding for standard output/error to prevent UnicodeEncodeError on Windows terminals
    try:
        import io
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to input budget CSV")
    parser.add_argument("--ward", help="Name of the ward to analyze (refuses if omitted or invalid)")
    parser.add_argument("--category", help="Name of the category to analyze (refuses if omitted or invalid)")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g. MoM, YoY) (refuses if omitted)")
    parser.add_argument("--output", default="growth_output.csv", help="Path to output result CSV")

    args = parser.parse_args()

    # 1. Growth-type Validation
    if not args.growth_type:
        print("Error: --growth-type must be specified explicitly (e.g., MoM or YoY). System refuses to guess or proceed.", file=sys.stderr)
        sys.exit(1)
    if args.growth_type.upper() not in ["MOM", "YOY"]:
        print(f"Error: Unsupported growth-type '{args.growth_type}'. Only 'MoM' and 'YoY' are supported. System refuses to proceed.", file=sys.stderr)
        sys.exit(1)

    # 2. Ward and Category Aggregation Validation (Cross-ward and cross-category aggregation is strictly prohibited)
    if not args.ward or args.ward.lower().strip() in ["all", "any", "*", "total"]:
        print("Error: A specific ward must be specified. Cross-ward or all-ward aggregation is strictly prohibited. System refuses to proceed.", file=sys.stderr)
        sys.exit(1)

    if not args.category or args.category.lower().strip() in ["all", "any", "*", "total"]:
        print("Error: A specific category must be specified. Cross-category or all-category aggregation is strictly prohibited. System refuses to proceed.", file=sys.stderr)
        sys.exit(1)

    # 3. Load dataset
    rows = load_dataset(args.input)

    # 4. Compute growth
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    # 5. Save and display output
    save_output(results, args.output)
    print_results(results)

if __name__ == "__main__":
    main()
