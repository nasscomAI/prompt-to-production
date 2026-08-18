"""
UC-0C app.py — Number That Looks Right.
Calculates per-period budget spend growth (MoM or YoY) for a specific ward and category.
Refuses all-ward or all-category aggregations, flags missing data rows, and displays
exact calculation formulas alongside output growth values.
"""
import argparse
import csv
import os
import sys

def load_dataset(file_path: str) -> list:
    """
    Reads the input budget CSV, validates columns, counts null actual spend rows,
    and reports them before returning.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    dataset = []

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Validate columns
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing headers.")
        
        missing_cols = [col for col in required_columns if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(f"Missing required columns in CSV: {missing_cols}")

        for row in reader:
            dataset.append(row)

    # Count and report null actual spend rows
    null_rows = []
    for i, row in enumerate(dataset, start=2): # 1-based index with header being line 1
        actual_spend = row['actual_spend'].strip()
        if not actual_spend:
            null_rows.append({
                'line': i,
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'notes': row['notes']
            })

    print(f"Dataset successfully loaded from {file_path}.")
    print(f"Total rows: {len(dataset)}")
    print(f"Total null actual_spend rows: {len(null_rows)}")
    for nr in null_rows:
        print(f"  - Line {nr['line']}: Period={nr['period']}, Ward='{nr['ward']}', Category='{nr['category']}'. Reason='{nr['notes']}'")

    return dataset

def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters data for the specified ward and category, identifies any null spend rows,
    and computes the growth rates (MoM or YoY) for each period, showing the formula used.
    """
    # Refuse invalid parameters
    if not ward or ward.lower() in ['any', 'all', 'any ward', 'all wards']:
        raise ValueError("All-ward aggregation is not allowed. A specific ward must be specified.")
    if not category or category.lower() in ['any', 'all', 'any category', 'all categories']:
        raise ValueError("All-category aggregation is not allowed. A specific category must be specified.")
    if growth_type not in ['MoM', 'YoY']:
        raise ValueError(f"Invalid growth type '{growth_type}'. Must be MoM or YoY.")

    # Filter the dataset
    filtered = [row for row in dataset if row['ward'] == ward and row['category'] == category]
    
    # Sort by period chronologically
    filtered.sort(key=lambda r: r['period'])

    output_rows = []
    
    # Helper to find a specific period's spend in the filtered slice
    def get_spend_for_period(target_period: str):
        for row in filtered:
            if row['period'] == target_period:
                spend_str = row['actual_spend'].strip()
                if not spend_str:
                    return None, "NULL", row['notes']
                try:
                    return float(spend_str), spend_str, row['notes']
                except ValueError:
                    return None, "INVALID", f"Invalid spend format: {spend_str}"
        return None, "MISSING", "Period not found in dataset"

    for row in filtered:
        period = row['period']
        spend_str = row['actual_spend'].strip()
        notes = row['notes'].strip()

        # Identify if current spend is null
        if not spend_str:
            output_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': f"NULL ({notes})",
                'formula': "N/A - Missing data",
                'notes': notes
            })
            continue

        current_spend = float(spend_str)

        # Determine target previous period
        if growth_type == 'MoM':
            # MoM growth: previous month
            parts = period.split('-')
            year = int(parts[0])
            month = int(parts[1])
            if month == 1:
                prev_year = year - 1
                prev_month = 12
            else:
                prev_year = year
                prev_month = month - 1
            prev_period = f"{prev_year:04d}-{prev_month:02d}"
            prev_period_desc = "previous month"
        else: # YoY
            # YoY growth: same month, previous year
            parts = period.split('-')
            year = int(parts[0])
            month = int(parts[1])
            prev_year = year - 1
            prev_period = f"{prev_year:04d}-{month:02d}"
            prev_period_desc = "previous year"

        prev_val, status, prev_notes = get_spend_for_period(prev_period)

        if status == "MISSING":
            output_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': spend_str,
                'growth': "N/A",
                'formula': f"N/A - {prev_period_desc} ({prev_period}) data missing",
                'notes': notes
            })
        elif status == "NULL":
            output_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': spend_str,
                'growth': "N/A",
                'formula': f"N/A - {prev_period_desc} ({prev_period}) actual spend is NULL due to: {prev_notes}",
                'notes': notes
            })
        elif status == "INVALID":
            output_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': spend_str,
                'growth': "N/A",
                'formula': f"N/A - {prev_period_desc} ({prev_period}) spend data is invalid",
                'notes': notes
            })
        else:
            diff = current_spend - prev_val
            growth_val = (diff / prev_val) * 100
            if growth_val > 0:
                growth_str = f"+{growth_val:.1f}%"
            elif growth_val < 0:
                growth_str = f"-{abs(growth_val):.1f}%"
            else:
                growth_str = "0.0%"

            formula_str = f"(({current_spend} - {prev_val}) / {prev_val}) * 100"
            output_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': spend_str,
                'growth': growth_str,
                'formula': formula_str,
                'notes': notes
            })

    return output_rows

def write_output(output_rows: list, output_path: str):
    """
    Writes output rows to a CSV file.
    """
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    headers = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula', 'notes']
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)
    print(f"Successfully wrote output to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", default=None, help="Path to input budget CSV file")
    parser.add_argument("--ward", default=None, help="Ward name (aggregation not allowed)")
    parser.add_argument("--category", default=None, help="Category name (aggregation not allowed)")
    parser.add_argument("--growth-type", default=None, help="Growth calculation type: MoM or YoY")
    parser.add_argument("--output", default=None, help="Path to write the output CSV file")
    args = parser.parse_args()

    # Rule 4: If --growth-type not specified — refuse and ask, never guess
    if not args.growth_type:
        print("Refusal: --growth-type must be explicitly specified. Choose MoM or YoY.")
        sys.exit(1)

    if args.growth_type not in ['MoM', 'YoY']:
        print(f"Refusal: Invalid --growth-type '{args.growth_type}'. Choose MoM or YoY.")
        sys.exit(1)

    # Rule 1: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not args.ward:
        print("Refusal: --ward must be explicitly specified to avoid ward aggregation.")
        sys.exit(1)
    if args.ward.lower() in ['any', 'all', 'any ward', 'all wards']:
        print("Refusal: All-ward aggregation is explicitly prohibited.")
        sys.exit(1)

    if not args.category:
        print("Refusal: --category must be explicitly specified to avoid category aggregation.")
        sys.exit(1)
    if args.category.lower() in ['any', 'all', 'any category', 'all categories']:
        print("Refusal: All-category aggregation is explicitly prohibited.")
        sys.exit(1)

    if not args.input:
        print("Refusal: --input path is required.")
        sys.exit(1)

    if not args.output:
        print("Refusal: --output path is required.")
        sys.exit(1)

    try:
        dataset = load_dataset(args.input)
        
        # Additional validation: check if specified ward/category exists in dataset
        unique_wards = sorted(list(set(row['ward'] for row in dataset)))
        unique_categories = sorted(list(set(row['category'] for row in dataset)))

        if args.ward not in unique_wards:
            print(f"Refusal: Specified ward '{args.ward}' does not exist in the dataset.")
            print(f"Available wards: {unique_wards}")
            sys.exit(1)

        if args.category not in unique_categories:
            print(f"Refusal: Specified category '{args.category}' does not exist in the dataset.")
            print(f"Available categories: {unique_categories}")
            sys.exit(1)

        output_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
        write_output(output_rows, args.output)

    except Exception as e:
        print(f"Error occurred during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
