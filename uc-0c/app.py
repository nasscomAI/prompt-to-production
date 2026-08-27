"""
UC-0C app.py — Budget Growth Data Analyst
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys

def load_dataset(filepath: str) -> list:
    """
    Reads the CSV dataset, validates columns, and explicitly reports the total 
    null count and which specific rows are null before returning the data.
    """
    data = []
    null_count = 0
    null_reports = []
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            if not row.get("actual_spend") or row["actual_spend"].strip() == "":
                null_count += 1
                null_reports.append(
                    f"Null detected in {row['period']} for {row['ward']} - {row['category']}. Reason: {row.get('notes', 'No notes provided')}"
                )
    
    print(f"--- DATA QUALITY REPORT ---")
    print(f"Total rows loaded: {len(data)}")
    print(f"Null values detected: {null_count}")
    if null_count > 0:
        for report in null_reports:
            print(f"  > {report}")
    print(f"---------------------------\n")
    
    return data

def compute_growth(dataset: list, target_ward: str, target_category: str, growth_type: str) -> list:
    """
    Takes the ward, category, and explicitly provided growth_type to calculate growth.
    Returns a per-period table with the formula used shown on each row.
    """
    # Enforcement: "If --growth-type is not specified, refuse and ask the user to specify it. Never guess"
    if not growth_type:
        print("ERROR: --growth-type must be explicitly provided (e.g., MoM or YoY). Refusing to guess.")
        sys.exit(1)
        
    if growth_type not in ["MoM", "YoY"]:
        print(f"ERROR: Unsupported growth type '{growth_type}'. Please explicitly request 'MoM' or 'YoY'.")
        sys.exit(1)
        
    # Enforcement: "Never aggregate across wards or categories unless explicitly instructed — refuse if asked."
    if not target_ward or target_ward.lower() == "all" or target_ward.lower() == "any":
        print("ERROR: Aggregation across different wards is not permitted without explicit instruction. Refusing.")
        sys.exit(1)
        
    if not target_category or target_category.lower() == "all" or target_category.lower() == "any":
        print("ERROR: Aggregation across different categories is not permitted. Refusing.")
        sys.exit(1)
        
    # Filter dataset
    filtered = [row for row in dataset if row["ward"] == target_ward and row["category"] == target_category]
    
    if not filtered:
        print(f"WARNING: No matching data found for Ward: '{target_ward}' and Category: '{target_category}'")
        return []
        
    # Sort chronologically
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual_str = current["actual_spend"].strip()

        # Enforcement: Flag every null row before computing
        if not actual_str:
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": "NULL",
                "growth": "FLAGGED: Not Computed",
                "formula": f"Refused computation due to missing data. Reason: {current.get('notes', '')}"
            })
            continue
            
        current_val = float(actual_str)
        
        # Calculate based on growth type
        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period,
                    "ward": target_ward,
                    "category": target_category,
                    "actual_spend": current_val,
                    "growth": "N/A",
                    "formula": "First period available; cannot compute MoM."
                })
            else:
                prev = filtered[i-1]
                prev_actual_str = prev["actual_spend"].strip()
                
                if not prev_actual_str:
                    results.append({
                        "period": period,
                        "ward": target_ward,
                        "category": target_category,
                        "actual_spend": current_val,
                        "growth": "N/A",
                        "formula": "Previous month was NULL; cannot compute MoM."
                    })
                else:
                    prev_val = float(prev_actual_str)
                    if prev_val == 0:
                        growth_val = 0.0
                    else:
                        growth_val = ((current_val - prev_val) / prev_val) * 100
                    
                    formula_str = f"MoM = (({current_val} - {prev_val}) / {prev_val}) * 100"
                    
                    results.append({
                        "period": period,
                        "ward": target_ward,
                        "category": target_category,
                        "actual_spend": current_val,
                        "growth": f"{growth_val:+.1f}%",
                        "formula": formula_str
                    })
        elif growth_type == "YoY":
            # Just an example YoY implementation stub assuming previous 12 months offset
            if i < 12:
                results.append({
                    "period": period,
                    "ward": target_ward,
                    "category": target_category,
                    "actual_spend": current_val,
                    "growth": "N/A",
                    "formula": "Insufficient historic data for YoY."
                })
            else:
                # Logic to find exact month last year goes here
                pass
                
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Output Tool")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=True, help="Target Ward to analyze")
    parser.add_argument("--category", required=True, help="Target Category to analyze")
    parser.add_argument("--growth-type", required=False, help="Explicit growth formula to use (e.g., MoM)")
    parser.add_argument("--output", required=True, help="Path to write the results CSV")
    args = parser.parse_args()
    
    # Trigger 1: Refusing to compute if growth-type is missing (handled implicitly in compute_growth too, but checked early here)
    if not args.growth_type:
        print("ERROR: Agent refused: Please explicitly request --growth-type (e.g. MoM). I will not assume a formula.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No results to write. Exiting.")
        sys.exit(0)
        
    # Write output properly showing the explicit formulas used per row
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
            
    print(f"Successfully calculated specific growth metrics and saved to {args.output}")

if __name__ == "__main__":
    main()
