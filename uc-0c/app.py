"""
UC-0C Budget Growth Analyst
Implementation based on RICE (agents.md) and skills.md.
"""
import argparse
import csv
import os

def load_dataset(file_path: str) -> list:
    """
    Reads CSV, validates columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    data = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_cols = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
        fieldnames = [h for h in (reader.fieldnames or [])]
        if not all(col in fieldnames for col in required_cols):
             raise ValueError(f"CSV missing mandatory columns. Required: {required_cols}")
        
        for row in reader:
            data.append(row)
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM/YoY growth for a specific ward and category.
    """
    if not ward or not category:
        raise ValueError("Specific 'ward' and 'category' must be provided. City-wide aggregation is prohibited.")

    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Growth type '{growth_type}' is invalid or missing. Must be MoM or YoY.")

    # Filter data
    filtered = [
        row for row in data 
        if row["ward"] == ward and row["category"] == category
    ]

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_actual = None

    for i, row in enumerate(filtered):
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        current_actual = None
        if actual_str:
            try:
                current_actual = float(actual_str)
            except ValueError:
                current_actual = None

        growth_val = "N/A"
        formula = "N/A"
        
        if current_actual is None:
            growth_val = f"NULL ({notes})"
            formula = "N/A (Missing Data)"
        elif prev_actual is None:
            growth_val = "N/A"
            formula = "Baseline (First Period/Prev Null)"
        else:
            # Calculate growth
            diff = current_actual - prev_actual
            growth = (diff / prev_actual) * 100
            growth_val = f"{growth:+.1f}%"
            formula = f"({current_actual} - {prev_actual}) / {prev_actual}"

        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": actual_str if actual_str else "NULL",
            "Growth": growth_val,
            "Formula": formula,
            "Notes": notes
        })
        
        # Update prev_actual for next iteration (M-o-M)
        # If we had a null, prev_actual remains None for the next one too? 
        # Usually MoM requires the immediate previous.
        prev_actual = current_actual

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        # Strict Enforcement Refusals
        if not args.ward or "all" in args.ward.lower():
            print("REFUSAL: City-wide aggregation across wards is not permitted.")
            return
        if not args.category or "all" in args.category.lower():
            print("REFUSAL: Aggregation across categories is not permitted.")
            return
        if args.growth_type not in ["MoM", "YoY"]:
             print("REFUSAL: Growth type must be MoM or YoY. Guessing is not allowed.")
             return

        data = load_dataset(args.input)
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if not results:
            print(f"No data found for Ward: {args.ward}, Category: {args.category}")
            return

        with open(args.output, mode='w', encoding='utf-8', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
                
        print(f"Growth calculation success. Results written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
