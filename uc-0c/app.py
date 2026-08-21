import argparse
import csv
import sys

def load_dataset(filepath: str, ward: str, category: str):
    """
    Reads CSV, validates columns, reports null count.
    Refuses cross-ward aggregation.
    """
    if ward.lower() == "any" or ward.lower() == "all" or category.lower() == "any" or category.lower() == "all":
        print("REFUSAL: Never aggregate across wards or categories unless explicitly instructed. Please specify a single ward and category.")
        sys.exit(1)
        
    filtered_data = []
    null_report = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ward'] == ward and row['category'] == category:
                    filtered_data.append(row)
                    if not row['actual_spend'].strip():
                        null_report.append((row['period'], row['notes']))
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        sys.exit(1)
        
    if null_report:
        print(f"Alert: Found {len(null_report)} null values in the requested data:")
        for period, note in null_report:
            print(f"  - {period}: {note}")
            
    return filtered_data

def compute_growth(data: list, growth_type: str) -> list:
    """
    Computes growth per period, shows formula, handles nulls.
    """
    if growth_type.upper() != "MOM":
        print(f"REFUSAL: Unsupported growth type '{growth_type}'. Cannot guess formula.")
        sys.exit(1)
        
    results = []
    # Data is assumed strictly sorted by period chronologically for MoM
    data.sort(key=lambda x: x['period'])
    
    for i in range(len(data)):
        current = data[i]
        period = current['period']
        ward = current['ward']
        category = current['category']
        spend_str = current['actual_spend'].strip()
        
        if not spend_str:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "Growth": f"Must be flagged — not computed. Reason: {current['notes']}"
            })
            continue
            
        current_spend = float(spend_str)
        
        # Need previous month for MoM
        if i == 0:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": current_spend,
                "Growth": "n/a (Formula: No previous data)"
            })
            continue
            
        prev = data[i-1]
        prev_spend_str = prev['actual_spend'].strip()
        
        if not prev_spend_str:
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": current_spend,
                "Growth": "n/a (Formula: Previous period is null)"
            })
            continue
            
        prev_spend = float(prev_spend_str)
        growth_val = ((current_spend - prev_spend) / prev_spend) * 100
        sign = "+" if growth_val >= 0 else ""
        formula_str = f"Formula: {growth_type} = ({current_spend} - {prev_spend}) / {prev_spend}"
        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": current_spend,
            "Growth": f"{sign}{growth_val:.1f}% ({formula_str})"
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, help="Must specify growth type (e.g. MoM)")
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    data = load_dataset(args.input, args.ward, args.category)
    results = compute_growth(data, args.growth_type)
    
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "Growth"]
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Processed {len(results)} periods for {args.ward} - {args.category}.")
    print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()
