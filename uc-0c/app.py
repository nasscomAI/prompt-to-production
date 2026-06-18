import argparse
import csv
import sys
import os

def load_dataset(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: Input file not found at {file_path}", file=sys.stderr)
        sys.exit(1)
        
    rows = []
    null_count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1-based line number (header is line 1)
            actual_spend_str = row.get("actual_spend", "").strip()
            if not actual_spend_str:
                null_count += 1
                row["actual_spend"] = None
                print(f"Flagged null row: line {i}, period={row['period']}, ward={row['ward']}, category={row['category']}, notes={row['notes']}")
            else:
                try:
                    row["actual_spend"] = float(actual_spend_str)
                except ValueError:
                    row["actual_spend"] = None
                    null_count += 1
                    print(f"Flagged null row (invalid float): line {i}, period={row['period']}, ward={row['ward']}, category={row['category']}, notes={row['notes']}")
            rows.append(row)
            
    print(f"Dataset loaded. Total rows: {len(rows)}, Flagged null rows: {null_count}")
    return rows

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--growth-type", default=None)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # 1. Enforce --growth-type must be specified
    if not args.growth_type:
        print("Error: --growth-type parameter is not specified. Refusing to guess. Please specify MoM or YoY.", file=sys.stderr)
        sys.exit(1)
        
    # 2. Reject all-ward or all-category aggregation requests
    if args.ward is None or args.ward.strip() == "" or args.ward.lower() in ["any", "all", "total"]:
        print("Error: All-ward aggregation or missing ward is not allowed. The system refuses to aggregate across multiple wards.", file=sys.stderr)
        sys.exit(1)
        
    if args.category is None or args.category.strip() == "" or args.category.lower() in ["any", "all", "total"]:
        print("Error: All-category aggregation or missing category is not allowed. The system refuses to aggregate across multiple categories.", file=sys.stderr)
        sys.exit(1)
        
    # 3. Load dataset
    dataset = load_dataset(args.input)
    
    # 4. Filter dataset for specific ward and category
    filtered = [r for r in dataset if r["ward"] == args.ward and r["category"] == args.category]
    
    if not filtered:
        print(f"Error: No records found matching ward='{args.ward}' and category='{args.category}'.", file=sys.stderr)
        sys.exit(1)
        
    # Sort by period (YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    output_rows = []
    
    for idx, row in enumerate(filtered):
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]
        
        # Calculate growth
        growth = "n/a"
        formula = "n/a"
        
        if actual_spend is None:
            growth = "NULL"
            formula = "n/a (current actual spend is null)"
        else:
            if idx == 0:
                growth = "n/a"
                formula = "n/a (no previous month)"
            else:
                prev_row = filtered[idx - 1]
                prev_spend = prev_row["actual_spend"]
                if prev_spend is None:
                    growth = "n/a"
                    formula = "n/a (previous month spend is null)"
                    if not notes:
                        notes = "Previous month's actual spend was null"
                else:
                    diff = actual_spend - prev_spend
                    pct = (diff / prev_spend) * 100
                    sign = "+" if pct >= 0 else ""
                    growth = f"{sign}{pct:.1f}%"
                    formula = f"(({actual_spend:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}) * 100"
                    
        output_rows.append({
            "period": period,
            "ward": args.ward,
            "category": args.category,
            "actual_spend": "NULL" if actual_spend is None else str(actual_spend),
            "growth_type": args.growth_type,
            "growth": growth,
            "formula": formula,
            "notes": notes
        })
        
    # Write to output file
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth", "formula", "notes"]
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
        
    print(f"Growth calculation results successfully written to {args.output}")

if __name__ == "__main__":
    main()
