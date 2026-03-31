import argparse
import csv
import sys
import logging

logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

def load_dataset(input_file, target_ward, target_category):
    """
    Safely reads CSV, validates ward/category, and filters out the matching dataset.
    """
    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        sys.exit(1)

    valid_wards = set()
    valid_categories = set()
    filtered_data = []

    for row in data:
        valid_wards.add(row['ward'])
        valid_categories.add(row['category'])
        
        if row['ward'] == target_ward and row['category'] == target_category:
            filtered_data.append(row)

    # Refuse invalid ward/category
    if target_ward not in valid_wards:
        logging.error(f"Invalid ward: '{target_ward}'. Available wards: {sorted(list(valid_wards))}")
        sys.exit(1)

    if target_category not in valid_categories:
        logging.error(f"Invalid category: '{target_category}'. Available categories: {sorted(list(valid_categories))}")
        sys.exit(1)

    # Sort data chronologically to ensure MoM computation is sequential
    filtered_data.sort(key=lambda x: x['period'])
    return filtered_data

def compute_growth(filtered_data):
    """
    Strictly computes Month-over-Month growth and flags silent null assumptions.
    """
    results = []
    prev_spend = None

    for row in filtered_data:
        period = row['period']
        actual_spend_str = row.get('actual_spend', '').strip()
        
        # Null handling validation: missing rows must be flagged
        if not actual_spend_str:
            logging.error(f"Data missing/null for period {period}. Notes: '{row.get('notes', '')}'. Cannot compute MoM.")
            sys.exit(1)
        
        try:
            actual_spend = float(actual_spend_str)
        except ValueError:
            logging.error(f"Invalid actual_spend value '{actual_spend_str}' for period {period}.")
            sys.exit(1)

        mom_growth_absolute = ""
        mom_growth_percent = ""
        
        if prev_spend is not None:
             # exact MoM formula
             growth = actual_spend - prev_spend
             mom_growth_absolute = round(growth, 2)
             if prev_spend != 0:
                 pct = (growth / prev_spend) * 100
                 mom_growth_percent = round(pct, 2)
             else:
                 mom_growth_percent = "N/A"
        
        results.append({
            'period': period,
            'ward': row['ward'],
            'category': row['category'],
            'actual_spend': actual_spend,
            'mom_growth_absolute': mom_growth_absolute,
            'mom_growth_percentage': mom_growth_percent
        })
        
        prev_spend = actual_spend

    return results

def main():
    parser = argparse.ArgumentParser(description="Compute MoM growth for ward budget.")
    parser.add_argument('--input', required=True, help="Path to input CSV")
    parser.add_argument('--ward', required=True, help="Ward name to filter")
    parser.add_argument('--category', required=True, help="Category name to filter")
    parser.add_argument('--growth-type', required=True, choices=['MoM'], help="Type of growth to compute")
    parser.add_argument('--output', required=True, help="Path to output CSV")

    args = parser.parse_args()

    # Step 1: Load and filter data securely (Only selected ward, Only selected category, No global aggregation)
    filtered_data = load_dataset(args.input, args.ward, args.category)

    # Step 2: Compute logic with exact formulas and Null handling
    results = compute_growth(filtered_data)

    # Step 3: Securely write the output
    try:
        with open(args.output, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['period', 'ward', 'category', 'actual_spend', 'mom_growth_absolute', 'mom_growth_percentage']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows. Output saved to {args.output}")
    except Exception as e:
        logging.error(f"Failed to write output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

