"""
UC-0C app.py — Ward Budget Analyst
Implemented based on RICE enforcement rules for granular budget auditing.
Consolidates all wards and categories into a single granular table if requested.
"""
import argparse
import csv
import os

def load_dataset(input_path: str) -> list:
    """Read CSV and report null actual_spend rows."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset {input_path} not found.")

    data = []
    null_rows = []
    with open(input_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Clean numerical values
            try:
                row['actual_spend'] = float(row['actual_spend']) if row['actual_spend'].strip() else None
            except ValueError:
                row['actual_spend'] = None
            
            if row['actual_spend'] is None:
                null_rows.append(f"Row {i+2}: {row['period']} | {row['ward']} | {row['category']} (Reason: {row['notes']})")
            
            data.append(row)
    
    if null_rows:
        print("IDENTIFIED NULL ACTUAL_SPEND VALUES:")
        for r in null_rows:
            print(f"  - {r}")
            
    return data

def compute_growth_for_pair(data: list, ward: str, category: str, growth_type: str) -> list:
    """Compute granular growth (MoM) for a specific ward/category pair."""
    # Strict matching (No aggregation)
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    if not filtered:
        return []

    # Sort by period to ensure sequential growth
    filtered.sort(key=lambda x: x['period'])

    results = []
    for i, row in enumerate(filtered):
        current_actual = row['actual_spend']
        period = row['period']
        notes = row['notes']
        
        growth_str = "n/a"
        formula = "n/a (First Period)"
        
        if i > 0:
            prev_actual = filtered[i-1]['actual_spend']
            if current_actual is None or prev_actual is None:
                growth_str = "NULL"
                formula = "Cannot compute (Null Value)"
                if current_actual is None:
                    # Current is null, use current notes
                    pass 
                else:
                    # Prev was null
                    notes = f"Preceding month ({filtered[i-1]['period']}) had null spend"
            else:
                diff = current_actual - prev_actual
                growth = (diff / prev_actual) * 100
                prefix = "+" if growth > 0 else ""
                growth_str = f"{prefix}{growth:.1f}%"
                formula = f"(Actual[{period}] - Actual[{filtered[i-1]['period']}]) / Actual[{filtered[i-1]['period']}]"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": current_actual if current_actual is not None else "NULL",
            "growth": growth_str,
            "formula": formula,
            "notes": notes
        })

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (specify 'All' for full breakdown)")
    parser.add_argument("--category", required=True, help="Category name (specify 'All' for full breakdown)")
    parser.add_argument("--growth-type", help="Growth calculation type (e.g. MoM)")
    parser.add_argument("--output", required=True, help="Path for growth_output.csv")
    
    args = parser.parse_args()

    # Enforcement: Refuse if growth-type is missing
    if not args.growth_type:
        print("REFUSAL: Growth calculation requested without specifying --growth-type (e.g., MoM). Please specify.")
        return

    try:
        data = load_dataset(args.input)
        
        # Batch Handling: Find unique values if "All" is specified
        target_wards = [args.ward] if args.ward.lower() != "all" else sorted(list(set(r['ward'] for r in data)))
        target_categories = [args.category] if args.category.lower() != "all" else sorted(list(set(r['category'] for r in data)))

        consolidated_results = []
        for ward in target_wards:
            for category in target_categories:
                consolidated_results.extend(compute_growth_for_pair(data, ward, category, args.growth_type))
        
        if consolidated_results:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "notes"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(consolidated_results)
            print(f"Done. Granular growth analysis for {len(consolidated_results)} rows written to {args.output}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
