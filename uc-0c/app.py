import argparse
import csv
import os

def load_dataset(file_path: str):
    """
    Reads the budget CSV and validates columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    
    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data, ward, category, growth_type):
    """
    Calculates MoM growth for a specific ward and category.
    """
    if ward.lower() == "all" or category.lower() == "all":
        return "ERROR: Aggregation across all wards or categories is not permitted. Please specify a single ward and category."

    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    if not filtered_data:
        return f"ERROR: No data found for Ward: '{ward}' and Category: '{category}'."

    # Sort by period to ensure correct MoM calculation
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    previous_spend = None

    for row in filtered_data:
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row['notes']
        
        result_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend_str if actual_spend_str else "NULL",
            "growth": "N/A",
            "formula": "n/a",
            "status": "OK"
        }

        if not actual_spend_str:
            result_row["growth"] = "NULL FLAG"
            result_row["formula"] = "n/a"
            result_row["status"] = f"FLAGGED: {notes}"
            previous_spend = None # Reset for next month if null
        else:
            current_spend = float(actual_spend_str)
            if previous_spend is not None:
                if growth_type == "MoM":
                    growth = ((current_spend - previous_spend) / previous_spend) * 100
                    result_row["growth"] = f"{growth:+.1f}%"
                    result_row["formula"] = f"({current_spend} - {previous_spend}) / {previous_spend} * 100"
                else:
                    result_row["growth"] = "ERROR: Unsupported growth type"
            
            previous_spend = current_spend

        results.append(result_row)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type must be specified (e.g., MoM). Refusing to guess.")
        exit(1)

    try:
        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if isinstance(results, str): # Error message
            print(results)
            exit(1)
            
        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "status"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Done. Growth analysis written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
