import argparse
import sys
import csv

def load_dataset(filepath, target_ward, target_category):
    """
    Skill: load_dataset
    Reads the CSV and applies filtering based on specific ward and category.
    Rule 1: Refusing to aggregate, only process the specific ward and category.
    """
    filtered_data = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Rule 1: Only process the specific --ward and --category requested
                if row.get('ward') == target_ward and row.get('category') == target_category:
                    filtered_data.append(row)
    except FileNotFoundError:
        print(f"Error: Dataset {filepath} not found.")
        sys.exit(1)
    return filtered_data

def compute_growth(previous_spend, current_spend):
    """
    Skill: compute_growth
    Calculates Month-over-Month (MoM) growth.
    """
    try:
        prev = float(previous_spend)
        curr = float(current_spend)
        if prev == 0:
            return None
        # Rule 4 compliance structure implemented here
        return ((curr - prev) / prev) * 100
    except (ValueError, TypeError):
        return None

def main():
    # Rule 1: Use argparse for: --input, --ward, --category, --growth-type, and --output.
    parser = argparse.ArgumentParser(description="Budget Analysis Agent (Financial Data Integrity Agent)")
    parser.add_argument("--input", default="../data/budget/ward_budget.csv", help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Specific ward to process")
    parser.add_argument("--category", required=True, help="Specific category to process")
    parser.add_argument("--growth-type", help="Type of growth calculation")
    parser.add_argument("--output", help="Path to output CSV")

    args = parser.parse_args()

    # Rule 5: If --growth-type is missing, exit and ask the user for it.
    if not args.growth_type:
        print("Error: --growth-type parameter is missing.")
        print("Please provide --growth-type to proceed with the execution.")
        sys.exit(1)

    print("ROLE: Financial Data Integrity Agent")
    print(f"Processing Filter - Ward: {args.ward}, Category: {args.category} (Aggregation strictly refused)")

    data = load_dataset(args.input, args.ward, args.category)

    if not data:
        print("No data found for the specified ward and category.")
        sys.exit(0)

    fieldnames = list(data[0].keys())
    if "MoM_Growth" not in fieldnames:
        fieldnames.extend(["MoM_Growth", "Formula_Used", "Flag"])

    results = []
    previous_spend = None

    for row in data:
        current_spend_raw = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        
        result_row = row.copy()
        # Rule 4: You MUST show the formula used: ((Current - Previous) / Previous) * 100 in every output row.
        result_row['Formula_Used'] = "((Current - Previous) / Previous) * 100"
        result_row['MoM_Growth'] = ""
        result_row['Flag'] = ""

        # Rule 2: If any actual_spend is null, you must FLAG it and report the 'notes' column for that row.
        # Do not calculate growth for null rows.
        if not current_spend_raw or current_spend_raw.lower() in ['null', 'none']:
            result_row['Flag'] = f"FLAGGED: actual_spend is null. Notes: {notes}"
            print(result_row['Flag'])
            previous_spend = None  # Reset previous spend due to disconnected period
        else:
            if previous_spend is not None:
                # Rule 3: Use compute_growth skill to calculate Month-over-Month (MoM) growth
                growth = compute_growth(previous_spend, current_spend_raw)
                if growth is not None:
                    result_row['MoM_Growth'] = f"{growth:.2f}%"
            previous_spend = current_spend_raw

        results.append(result_row)

    if args.output:
        try:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Results successfully saved to {args.output}")
        except IOError as e:
            print(f"Failed to write output to {args.output}: {e}")
    else:
        for r in results:
            print(r)

if __name__ == "__main__":
    main()
