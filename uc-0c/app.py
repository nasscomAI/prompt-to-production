import csv
import argparse
import os

def load_dataset(file_path):
    if not os.path.exists(file_path):
        return None, f"Error: File {file_path} not found."
    
    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data, None

def compute_growth(data, ward, category, growth_type, output_file):
    if not growth_type:
        print("Error: --growth-type must be specified (MoM or YoY).")
        return

    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period
    filtered_data.sort(key=lambda x: x['period'])
    
    results = []
    previous_spend = None
    
    for i, row in enumerate(filtered_data):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        notes = row.get('notes', '')
        
        actual_spend = None
        growth_pct = "N/A"
        formula = "N/A"
        status = ""
        
        if not actual_spend_str:
            status = f"NULL - {notes}"
        else:
            try:
                actual_spend = float(actual_spend_str)
                if i > 0 and previous_spend is not None:
                    # MoM Growth
                    if growth_type == "MoM":
                        growth = ((actual_spend - previous_spend) / previous_spend) * 100
                        growth_pct = f"{growth:+.1f}%"
                        formula = f"(({actual_spend} - {previous_spend}) / {previous_spend}) * 100"
                
                previous_spend = actual_spend
            except ValueError:
                status = f"Invalid Spend - {actual_spend_str}"
                previous_spend = None

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend_str if actual_spend_str else "NULL",
            "growth_pct": growth_pct,
            "formula": formula,
            "status": status
        })

    # Write to CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "status"]
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Successfully computed {growth_type} growth -> {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute budget growth.")
    parser.add_argument("--input", required=True, help="Input budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Budget category")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Growth type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Output CSV file")
    
    args = parser.parse_args()
    
    data, error = load_dataset(args.input)
    if error:
        print(error)
    else:
        compute_growth(data, args.ward, args.category, args.growth_type, args.output)
