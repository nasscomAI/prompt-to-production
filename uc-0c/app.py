"""
UC-0C app.py — Budget Growth Calculator
Implemented using strict RICE constraints to prevent LLM calculation hallucinations.
"""
import argparse
import csv

def load_dataset(filepath: str) -> tuple[list[dict], list[dict]]:
    """
    Reads the budget CSV, validates columns, and performs a strict initial audit for null values.
    Returns: (validated_data, list_of_null_records)
    """
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    data = []
    null_records = []
    
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validation
        if not reader.fieldnames:
            raise ValueError("CSV is empty or unreadable.")
        for col in required_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing required column: {col}")
                
        # Load and audit
        for i, row in enumerate(reader):
            val = row.get("actual_spend", "").strip()
            if not val:
                null_records.append(row)
                row["actual_spend"] = None
            else:
                try:
                    row["actual_spend"] = float(val)
                except ValueError:
                    row["actual_spend"] = None
                    null_records.append(row)
            data.append(row)
            
    print(f"Dataset Audit: Total rows = {len(data)}, Null 'actual_spend' rows = {len(null_records)}")
    for r in null_records:
        print(f"  - NULL found: Period {r['period']}, Ward {r['ward']}, Category {r['category']}. Reason: '{r['notes']}'")
        
    return data, null_records

def compute_growth(data: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Calculates specified growth metric for a strictly defined ward and category.
    """
    if not ward or not category:
        raise ValueError("REFUSAL: Must specify an exact ward and category. Aggregation across multiple is forbidden.")
        
    if not growth_type:
        raise ValueError("REFUSAL: growth-type not specified. Cannot assume or default to a formula.")
        
    if growth_type.upper() != "MOM":
        raise ValueError(f"REFUSAL: Unsupported growth_type '{growth_type}'. Only MoM is currently implemented.")

    # Filter data
    filtered = [r for r in data if r["ward"] == ward and r["category"] == category]
    
    # Sort chronologically (period is YYYY-MM)
    filtered.sort(key=lambda x: x["period"])
    
    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        period = current["period"]
        actual = current["actual_spend"]
        
        result_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend": actual if actual is not None else "NULL",
            "Growth Type": growth_type,
            "Growth Value": "N/A",
            "Formula": "N/A",
            "Flags/Notes": ""
        }
        
        if actual is None:
            result_row["Flags/Notes"] = f"FLAGGED NULL: {current['notes']}"
            result_row["Formula"] = "Cannot compute (Current month is NULL)"
            results.append(result_row)
            continue
            
        if i == 0:
            result_row["Formula"] = "Cannot compute (No prior month data)"
            results.append(result_row)
            continue
            
        prev = filtered[i-1]
        prev_actual = prev["actual_spend"]
        
        if prev_actual is None:
            result_row["Flags/Notes"] = f"FLAGGED PREVIOUS NULL: {prev['notes']}"
            result_row["Formula"] = "Cannot compute (Prior month is NULL)"
            results.append(result_row)
            continue
            
        # Calculate MoM
        if prev_actual == 0:
            result_row["Formula"] = "Cannot compute (Prior month spend is 0)"
            results.append(result_row)
            continue
            
        growth = ((actual - prev_actual) / prev_actual) * 100
        result_row["Growth Value"] = f"{growth:+.1f}%"
        result_row["Formula"] = f"(({actual} - {prev_actual}) / {prev_actual}) * 100"
        
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, help="Target ward (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Target category (e.g., 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g., 'MoM')")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()
    
    try:
        data, nulls = load_dataset(args.input)
        
        # This will trigger the enforcement rules and refuse if not provided
        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if results:
            fieldnames = ["Ward", "Category", "Period", "Actual Spend", "Growth Type", "Growth Value", "Formula", "Flags/Notes"]
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully wrote granular calculations to {args.output}")
            
    except Exception as e:
        print(f"\n[SYSTEM REFUSAL OR ERROR] {e}")

if __name__ == "__main__":
    main()
