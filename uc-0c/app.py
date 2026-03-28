import csv
import argparse
import sys

def load_dataset(input_path):
    """
    Loads the CSV dataset and identifies null actual_spend values.
    """
    data = []
    null_rows = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Clean up empty strings to None
                if not row['actual_spend']:
                    row['actual_spend'] = None
                    null_rows.append(row)
                else:
                    row['actual_spend'] = float(row['actual_spend'])
                data.append(row)
        return data, null_rows
    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

def compute_growth(data, ward, category, growth_type):
    """
    Computes MoM growth for a specific ward and category.
    """
    if not growth_type:
        print("Error: --growth-type must be specified (e.g., MoM). Refusing to guess.")
        sys.exit(1)
    
    if growth_type != "MoM":
        print(f"Error: Growth type '{growth_type}' is not supported yet. Use 'MoM'.")
        sys.exit(1)

    # Filter by ward and category
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"No data found for Ward: '{ward}', Category: '{category}'.")
        return []

    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    for i in range(len(filtered_data)):
        current = filtered_data[i]
        result = {
            "period": current['period'],
            "ward": current['ward'],
            "category": current['category'],
            "actual_spend": current['actual_spend'] if current['actual_spend'] is not None else "NULL",
            "growth": "N/A (First period)",
            "formula": "None",
            "notes": current['notes']
        }

        if i > 0:
            previous = filtered_data[i-1]
            if current['actual_spend'] is None:
                result["growth"] = "NULL: Cannot compute"
                result["formula"] = "N/A (Current value is NULL)"
            elif previous['actual_spend'] is None:
                result["growth"] = "NULL: Cannot compute"
                result["formula"] = "N/A (Previous value is NULL)"
            else:
                curr_val = current['actual_spend']
                prev_val = previous['actual_spend']
                growth_val = ((curr_val - prev_val) / prev_val) * 100
                result["growth"] = f"{growth_val:+.1f}%"
                result["formula"] = f"({curr_val} - {prev_val}) / {prev_val}"

        results.append(result)

    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Analyst.")
    parser.add_argument("--input", required=True, help="Path to input CSV.")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze.")
    parser.add_argument("--category", required=True, help="Specific category to analyze.")
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g., MoM).")
    parser.add_argument("--output", required=True, help="Path to output CSV.")
    
    args = parser.parse_args()
    
    data, null_rows = load_dataset(args.input)
    
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if results:
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Growth report generated: {args.output}")

if __name__ == "__main__":
    main()