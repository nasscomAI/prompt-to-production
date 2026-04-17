"""
UC-0C — Budget Analyst
Implemented based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

def load_dataset(input_path: str) -> list:
    """
    Reads CSV and validates required columns.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found.")
        
    data = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM growth for the specified ward and category.
    """
    if not growth_type:
        raise ValueError("Growth type not specified. Please specify MoM or YoY.")
    
    if growth_type != "MoM":
        raise NotImplementedError(f"Growth type '{growth_type}' is not yet supported. Only MoM is available.")

    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual_spend_str = current['actual_spend'].strip()
        
        # Handle Nulls
        if not actual_spend_str or actual_spend_str.upper() == "NULL":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "N/A",
                "formula": "N/A",
                "notes": f"DATA_GAP: {current.get('notes', 'No reason provided')}"
            })
            continue

        try:
            val_current = float(actual_spend_str)
        except ValueError:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend_str,
                "growth": "ERROR",
                "formula": "N/A",
                "notes": "Invalid numeric value"
            })
            continue

        # Compute growth if previous month exists and is valid
        growth_val = "First Month"
        formula = "N/A"
        
        if i > 0:
            prev = filtered[i-1]
            prev_spend_str = prev['actual_spend'].strip()
            
            if prev_spend_str and prev_spend_str.upper() != "NULL":
                try:
                    val_prev = float(prev_spend_str)
                    if val_prev != 0:
                        growth = ((val_current - val_prev) / val_prev) * 100
                        growth_val = f"{growth:+.1f}%"
                        formula = f"({val_current} - {val_prev}) / {val_prev}"
                    else:
                        growth_val = "INF"
                        formula = "Division by zero"
                except ValueError:
                    growth_val = "N/A (Prev Invalid)"
            else:
                growth_val = "N/A (Prev NULL)"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": val_current,
            "growth": growth_val,
            "formula": formula,
            "notes": current.get('notes', '')
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()

    try:
        if not args.growth_type:
            print("REJECTION: Growth type not specified. Please use --growth-type MoM or YoY.")
            return

        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"No data found for Ward: '{args.ward}' and Category: '{args.category}'")
            return

        fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Success. Analysis written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
