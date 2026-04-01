"""
UC-0C app.py — Ward Budget Analyst.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import os

def load_dataset(input_path: str) -> list:
    """
    Reads the ward budget CSV file and performs initial validation on the required columns and null values.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} not found.")
    
    data = []
    null_rows = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1-indexed Excel row starts at 2
            # Handle empty actual_spend
            actual_spend = row.get("actual_spend", "").strip()
            if not actual_spend:
                row["actual_spend"] = None
                null_rows.append(f"Row {i} ({row['period']}): {row.get('notes', 'No reason provided')}")
            else:
                try:
                    row["actual_spend"] = float(actual_spend)
                except ValueError:
                    row["actual_spend"] = None
                    null_rows.append(f"Row {i} ({row['period']}): Invalid numeric value")
            
            # Convert budgeted_amount
            try:
                row["budgeted_amount"] = float(row.get("budgeted_amount", 0))
            except ValueError:
                row["budgeted_amount"] = 0.0
                
            data.append(row)
            
    if null_rows:
        print(f"Dataset loaded. {len(null_rows)} null actual_spend rows identified:")
        for note in null_rows:
            print(f" - {note}")
    else:
        print("Dataset loaded successfully with no nulls.")
        
    return data


def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period growth (MoM) for a specific ward and category, flagging null values appropriately.
    """
    # Filter for the specific ward and category
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort by period to ensure MoM calculation order
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        curr = filtered[i]
        prev = filtered[i-1] if i > 0 else None
        
        growth_val = "n/a"
        formula = "n/a"
        
        # Computation only if not first month and growth_type matches
        if prev and growth_type == "MoM":
            curr_val = curr['actual_spend']
            prev_val = prev['actual_spend']
            
            if curr_val is None:
                growth_val = "NULL"
                formula = f"Cannot compute: {curr.get('notes', 'Current actual spend is missing')}"
            elif prev_val is None:
                growth_val = "NULL"
                formula = f"Cannot compute: {prev.get('notes', 'Previous actual spend was missing')}"
            else:
                try:
                    # Formula: (Current - Previous) / Previous
                    change = curr_val - prev_val
                    growth = (change / prev_val) * 100
                    growth_val = f"{'+' if growth >= 0 else ''}{growth:.1f}%"
                    formula = f"({curr_val} - {prev_val}) / {prev_val}"
                except ZeroDivisionError:
                    growth_val = "INF"
                    formula = "Division by zero (previous spend was 0)"
        elif i == 0:
            formula = "First period in filtered dataset"
            
        results.append({
            "period": curr['period'],
            "ward": curr['ward'],
            "category": curr['category'],
            "actual_spend": curr['actual_spend'] if curr['actual_spend'] is not None else "NULL",
            "growth": growth_val,
            "formula_shown": formula
        })
        
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name (e.g., 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific category name")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    # Enforcement Rule 4: Refuse if growth-type unspecified
    if not args.growth_type:
        print("Refusal: Growth type unspecified. Please specify MoM or YoY.")
        return

    # Enforcement Rule 1: Refuse aggregate requests (e.g., "Any")
    if "any" in args.ward.lower() or "any" in args.category.lower():
        print("Refusal: Aggregated analysis requested. I only provide per-ward, per-category breakdowns.")
        return

    try:
        data = load_dataset(args.input)
        
        # Verify ward and category exist
        wards = set(r['ward'] for r in data)
        categories = set(r['category'] for r in data)
        
        if args.ward not in wards:
            print(f"Error: Ward '{args.ward}' not found. Available: {', '.join(sorted(wards))}")
            return
        if args.category not in categories:
            print(f"Error: Category '{args.category}' not found. Available: {', '.join(sorted(categories))}")
            return

        results = compute_growth(data, args.ward, args.category, args.growth_type)
        
        if results:
            fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula_shown"]
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Done. Results written to {args.output}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
