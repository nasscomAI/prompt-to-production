import argparse
import csv
import sys

def compute_growth(input_file, ward, category, growth_type, output_file):
    if not input_file or not ward or not category or not growth_type or not output_file:
        print("Error: Missing required arguments. Please specify --ward, --category, and --growth-type.")
        sys.exit(1)
        
    if growth_type.lower() != "mom":
        print(f"Error: Growth type '{growth_type}' not supported or unrecognized.")
        sys.exit(1)
        
    if ward.lower() == "any" or category.lower() == "any":
        print("Error: System REFUSES to aggregate across wards or categories. Please specify an exact ward and category.")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        
    # Filter rows mapped to specified ward and category
    filtered = [r for r in all_rows if r["ward"].strip() == ward and r["category"].strip() == category]
    
    if not filtered:
        print(f"No data found for ward '{ward}' and category '{category}'.")
        sys.exit(1)
        
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered)):
        row = filtered[i]
        period = row["period"]
        actual_str = row["actual_spend"].strip()
        notes = row["notes"].strip()
        
        actual_val = None
        if actual_str:
            try:
                actual_val = float(actual_str)
            except ValueError:
                pass
                
        prev_val = None
        if i > 0:
            prev_str = filtered[i-1]["actual_spend"].strip()
            if prev_str:
                try:
                    prev_val = float(prev_str)
                except ValueError:
                    pass
                    
        # Reference value check: If actual spend is missing, it must be flagged
        if actual_val is None:
            growth_pct = "NULL"
            formula = "Cannot compute (Actual Spend is NULL)"
            spend_out = "NULL"
            warnings = f"FLAGGED: Data missing. Reason: {notes}"
        elif prev_val is None:
            growth_pct = "N/A"
            formula = "No previous month data"
            spend_out = f"{actual_val:.1f}"
            warnings = ""
        else:
            growth_val = ((actual_val - prev_val) / prev_val) * 100
            
            # Formatting identical to reference table (e.g., +33.1%)
            sign = "+" if growth_val >= 0 else ""
            growth_pct = f"{sign}{growth_val:.1f}%"
            formula = f"(({actual_val} - {prev_val}) / {prev_val}) * 100"
            spend_out = f"{actual_val:.1f}"
            warnings = ""

        results.append({
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (Lakh)": spend_out,
            "MoM Growth": growth_pct,
            "Formula": formula,
            "Flags/Notes": warnings
        })
        
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["Ward", "Category", "Period", "Actual Spend (Lakh)", "MoM Growth", "Formula", "Flags/Notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Success! Growth data written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)
