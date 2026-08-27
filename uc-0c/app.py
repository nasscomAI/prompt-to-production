"""
UC-0C — Number That Looks Right (MoM/YoY growth)
Implements load_dataset and compute_growth as defined in agents.md and skills.md.

This script calculates budget growth metric on a per-ward/per-category basis
and flags the 5 planned null rows with their specific rationale from the notes.
No models or ML used.
"""
import argparse
import csv
import os

# ---------------------------------------------------------------------------
# Skills implementation
# ---------------------------------------------------------------------------

def load_dataset(input_path: str) -> list:
    """
    Reads a CSV budget file and filters out ward/category/actual_spend columns.
    Reports any null actual_spend rows found during loading.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Budget file not found: {input_path}")

    rows = []
    null_count = 0
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2): # 1-indexed (header is 1)
            # Find the 5 deliberate null actual_spend values
            if not row['actual_spend']:
                null_count += 1
                period = row['period']
                ward = row['ward']
                cat = row['category']
                notes = row.get('notes', 'No reason logged')
                print(f"  [NULL FLAG] Row {i}: {period} | {ward} | {cat} -> Reason: {notes}")
            rows.append(row)
            
    print(f"Found {len(rows)} total rows, with {null_count} null actual_spend records.")
    return rows

def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Calculates MoM/YoY growth for a specific ward and category.
    Strictly refuses aggregation.
    """
    # Enforcement: No silent aggregation
    if not ward or not category:
        raise ValueError("Ward and Category must be specified; all-ward aggregation is not permitted.")
        
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Growth type '{growth_type}' not specified or invalid. Must be MoM or YoY.")

    # Filter to requested ward and category
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    
    # Sort by period to ensure correct growth sequence
    filtered.sort(key=lambda x: x['period'])
    
    if not filtered:
        print(f"  [WARNING] No data found for Ward='{ward}', Category='{category}'")
        return []

    results = []
    
    for i in range(len(filtered)):
        current = filtered[i]
        curr_val_str = current['actual_spend']
        period = current['period']
        
        # Rule 2: Flag null rows before computing
        if not curr_val_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_pct": "n/a",
                "formula": "n/a",
                "notes": current.get('notes', 'Data missing')
            })
            continue

        curr_val = float(curr_val_str)
        
        # Look for previous period row
        prev = None
        if growth_type == "MoM":
            if i > 0:
                prev = filtered[i-1]
        elif growth_type == "YoY":
            # Find row from 12 months prior
            parts = period.split('-')
            year = int(parts[0]) - 1
            prev_period = f"{year}-{parts[1]}"
            for r in filtered:
                if r['period'] == prev_period:
                    prev = r
                    break
        
        # Calculate growth if previous data exists and is not null
        if prev and prev['actual_spend']:
            prev_val = float(prev['actual_spend'])
            growth = ((curr_val - prev_val) / prev_val) * 100
            formula = f"({curr_val} - {prev_val}) / {prev_val}"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": curr_val,
                "growth_pct": f"{growth:+.1f}%",
                "formula": formula,
                "notes": current.get('notes', '')
            })
        else:
            reason = "First period" if not prev else f"Previous data missing ({prev['period']})"
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": curr_val,
                "growth_pct": "n/a",
                "formula": "n/a",
                "notes": f"{reason}; " + current.get('notes', '')
            })
            
    return results

# ---------------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Budget Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category")
    parser.add_argument("--growth-type", help="MoM or YoY (default MoM if not enforced, but we enforce it)")
    parser.add_argument("--output", required=True, help="Path to write the CSV results")
    
    args = parser.parse_args()

    # Rule 4: Refuse if growth-type unspecified
    if not args.growth_type:
        print("Error: Growth-type unspecified. Select MoM or YoY.")
        exit(1)

    try:
        print(f"Loading dataset: {args.input}")
        rows = load_dataset(args.input)
        
        print(f"Computing {args.growth_type} growth for Ward='{args.ward}' Category='{args.category}'")
        report = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        if not report:
            exit(1)
            
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            if report:
                writer = csv.DictWriter(f, fieldnames=report[0].keys())
                writer.writeheader()
                writer.writerows(report)
            
        print(f"Growth report written to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
