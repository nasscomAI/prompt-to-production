import argparse
import csv
import sys

def compute_growth(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    """
    Computes growth metrics with strict null handling and formula transparency.
    """
    if not growth_type:
        print("Error: --growth-type must be specified (e.g., MoM).")
        sys.exit(1)

    data = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # If ward/category specified, filter. Otherwise take all.
                if (not ward or row['ward'] == ward) and (not category or row['category'] == category):
                    data.append(row)
        
        if not data:
            print(f"No data found for Ward: {ward}, Category: {category}")
            return

        # Group data by (ward, category)
        grouped_data = {}
        for row in data:
            key = (row['ward'], row['category'])
            if key not in grouped_data:
                grouped_data[key] = []
            grouped_data[key].append(row)

        results = []
        for (w, c), group in grouped_data.items():
            # Sort group by period
            group.sort(key=lambda x: x['period'])
            
            prev_spend = None
            for row in group:
                period = row['period']
                actual_spend_str = row['actual_spend']
                notes = row['notes']
                
                result_row = {
                    "ward": w,
                    "category": c,
                    "period": period,
                    "actual_spend": actual_spend_str,
                    "growth": "n/a",
                    "formula": "n/a",
                    "notes": notes
                }

                if not actual_spend_str:
                    result_row["growth"] = "NULL"
                    result_row["formula"] = "Cannot compute (Null Value)"
                    results.append(result_row)
                    prev_spend = None
                    continue

                current_spend = float(actual_spend_str)
                
                if growth_type == "MoM":
                    if prev_spend is not None:
                        growth = ((current_spend - prev_spend) / prev_spend) * 100
                        result_row["growth"] = f"{growth:+.1f}%"
                        result_row["formula"] = f"({current_spend} - {prev_spend}) / {prev_spend}"
                    else:
                        result_row["growth"] = "n/a"
                        result_row["formula"] = "First period or previous null"
                    prev_spend = current_spend
                
                results.append(result_row)

        keys = results[0].keys()
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Growth report written to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Specific ward name")
    parser.add_argument("--category", help="Specific category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write CSV results")
    args = parser.parse_args()
    
    compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)
