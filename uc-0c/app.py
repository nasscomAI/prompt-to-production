import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Reads the ward budget CSV file and performs a pre-computation validation check 
    for column integrity and null value identification.
    """
    if not os.path.exists(filepath):
        print(f"Error: Input file {filepath} not found.")
        sys.exit(1)
        
    dataset = []
    null_rows = []
    
    expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if not expected_cols.issubset(set(reader.fieldnames)):
            print("Error: Missing required columns in dataset. Expected: period, ward, category, budgeted_amount, actual_spend, notes")
            sys.exit(1)
            
        for row in reader:
            if not row["actual_spend"].strip():
                null_rows.append(row)
            dataset.append(row)
            
    print(f"Dataset loaded. Total rows: {len(dataset)}")
    print(f"Null actual_spend rows found: {len(null_rows)}")
    for row in null_rows:
        print(f"  - {row['period']} | {row['ward']} | {row['category']} -> {row['notes']}")
        
    return dataset

def compute_growth(ward, category, growth_type, dataset, output_path):
    """
    Calculates period-over-period growth for a specific ward and category using an explicit 
    growth type while flagging rows where computation is impossible.
    """
    # Enforcement: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        print("Error: --growth-type parameter is missing. The agent refuses to guess. Please specify explicitly (e.g., MoM).")
        sys.exit(1)
        
    # Enforcement: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or ward.lower() in ("any", "all"):
        print("Error: All-ward aggregation or missing ward parameter detected. Refusing to aggregate across wards per enforcement rules.")
        sys.exit(1)
        
    if not category or category.lower() in ("any", "all"):
        print("Error: All-category aggregation or missing category parameter detected. Refusing to aggregate across categories per enforcement rules.")
        sys.exit(1)

    growth_type = growth_type.upper()
    if growth_type != "MOM":
        print(f"Error: Unsupported growth type '{growth_type}'. Only MoM is currently supported.")
        sys.exit(1)

    # Filter data to matching ward & category
    filtered_data = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: {ward}, Category: {category}")
        sys.exit(1)
        
    # Sort chronologically by period (e.g. 2024-01)
    filtered_data.sort(key=lambda x: x["period"])
    
    results = []
    for i in range(len(filtered_data)):
        current_row = filtered_data[i]
        period = current_row["period"]
        actual_spend_str = current_row["actual_spend"].strip()
        notes = current_row["notes"].strip()
        
        if i == 0:
            if not actual_spend_str:
                 results.append({
                     "Period": period,
                     "Actual Spend": "NULL",
                     "Growth Result": f"not computed, reason: {notes}",
                     "Formula Used": "N/A (Null value)"
                 })
            else:
                 results.append({
                     "Period": period,
                     "Actual Spend": actual_spend_str,
                     "Growth Result": "N/A",
                     "Formula Used": "N/A (First period)"
                 })
            continue

        prev_row = filtered_data[i-1]
        prev_spend_str = prev_row["actual_spend"].strip()
        
        # Determine if computation is possible
        if not actual_spend_str:
            # Enforcement: For specific known nulls ... the growth must be flagged as "not computed."
            results.append({
                "Period": period,
                "Actual Spend": "NULL",
                "Growth Result": f"not computed, reason: {notes}",
                "Formula Used": "N/A (Current month is null)"
             })
        elif not prev_spend_str:
            results.append({
                "Period": period,
                "Actual Spend": actual_spend_str,
                "Growth Result": "not computed: previous month is null",
                "Formula Used": "N/A (Previous month is null)"
            })
        else:
            try:
                curr_val = float(actual_spend_str)
                prev_val = float(prev_spend_str)
                if prev_val == 0:
                    results.append({
                        "Period": period,
                        "Actual Spend": f"{curr_val:.1f}",
                        "Growth Result": "N/A",
                        "Formula Used": f"({curr_val} - {prev_val}) / {prev_val} * 100 (Division by zero)"
                    })
                else:
                    # Enforcement: Show formula used in every output row alongside the result
                    pct = ((curr_val - prev_val) / prev_val) * 100
                    prefix = "+" if pct > 0 else ""
                    results.append({
                        "Period": period,
                        "Actual Spend": f"{curr_val:.1f}",
                        "Growth Result": f"{prefix}{pct:.1f}%",
                        "Formula Used": f"({curr_val} - {prev_val}) / {prev_val} * 100"
                    })
            except ValueError:
                results.append({
                    "Period": period,
                    "Actual Spend": actual_spend_str,
                    "Growth Result": "Error",
                    "Formula Used": "Data format error"
                })

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Period", "Actual Spend", "Growth Result", "Formula Used"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print(f"Growth calculation written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--output", required=True, help="Path to write the growth output")
    parser.add_argument("--ward", default=None, help="Specific ward to analyze")
    parser.add_argument("--category", default=None, help="Specific category to analyze")
    parser.add_argument("--growth-type", default=None, help="Type of growth calculation (e.g., MoM)")
    args = parser.parse_args()
    
    dataset = load_dataset(args.input)
    compute_growth(args.ward, args.category, args.growth_type, dataset, args.output)

if __name__ == "__main__":
    main()
