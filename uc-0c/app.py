import argparse
import csv
import sys

def run_naive(input_file, output_file):
    # Aggregating all wards and all categories, calculating a single growth
    # Skipping null check and formula declaration entirely.
    total_spend = 0
    with open(input_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['actual_spend'].strip():
                # Silently ignoring nulls
                total_spend += float(r['actual_spend'])
                
    # Silently picking arbitrary growth output
    with open(output_file, "w", encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Aggregated Total Spend", "Calculated Growth"])
        writer.writerow([round(total_spend, 2), "14.5%"])  # Hallucinated YoY

def run_rice(input_file, ward, category, growth_type, output_file):
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        print("REFUSED: Never aggregate across wards or categories unless explicitly instructed.")
        sys.exit(1)
        
    if not growth_type:
        print("REFUSED: --growth-type not specified. Please provide growth type, refusing to guess.")
        sys.exit(1)
        
    rows = []
    with open(input_file, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['ward'] == ward and r['category'] == category:
                rows.append(r)
                
    # Sort chronologically
    rows.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in rows:
        period = row['period']
        spend_str = row['actual_spend']
        notes = row['notes']
        
        if not spend_str.strip():
            # Flagged null row explicitly
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": "NULL",
                "MoM Growth": f"Must be flagged — not computed (Reason: {notes})"
            })
            prev_spend = None
        else:
            spend = float(spend_str)
            if prev_spend is None:
                growth_text = "N/A (base month)"
            else:
                growth = ((spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth > 0 else ""
                growth_text = f"{sign}{growth:.1f}% (formula: ({spend} - {prev_spend}) / {prev_spend})"
                
            results.append({
                "Ward": ward,
                "Category": category,
                "Period": period,
                "Actual Spend (₹ lakh)": spend_str,
                "MoM Growth": growth_text
            })
            prev_spend = spend
            
    fieldnames = ["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"]
    with open(output_file, "w", encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--growth-type", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", default="rice", choices=["naive", "rice"])
    args = parser.parse_args()

    if args.mode == "naive":
        run_naive(args.input, args.output)
    else:
        run_rice(args.input, args.ward, args.category, args.growth_type, args.output)

if __name__ == "__main__":
    main()
