"""
UC-0C app.py — Budget Growth Analyzer
Implementation based on RICE + agents.md + skills.md workflow.
"""
import argparse
import csv

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    data = []
    null_rows = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate actual_spend
                val = row.get('actual_spend', '').strip()
                if not val:
                    null_rows.append(row)
                data.append(row)
        
        print(f"Dataset loaded. Total rows: {len(data)}. Null actual_spend values found: {len(null_rows)}")
        for nr in null_rows:
            print(f"NULL found: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['notes']}")
            
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def compute_growth(data, ward, category, growth_type):
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    # Filter data for specific ward and category
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        current = filtered[i]
        period = current['period']
        actual = current['actual_spend'].strip()
        notes = current['notes']
        
        if i == 0:
            # First period has no previous for MoM
            results.append({
                'period': period,
                'actual_spend': actual if actual else 'NULL',
                'growth': 'N/A (First Period)',
                'formula': 'N/A'
            })
            continue
            
        prev = filtered[i-1]
        prev_actual = prev['actual_spend'].strip()
        
        if not actual or not prev_actual:
            # Handle NULLs
            reason = notes if not actual else prev['notes']
            results.append({
                'period': period,
                'actual_spend': actual if actual else 'NULL',
                'growth': 'NULL',
                'formula': f"Cannot compute due to NULL value. Reason: {reason}"
            })
        else:
            curr_val = float(actual)
            prev_val = float(prev_actual)
            growth = ((curr_val - prev_val) / prev_val) * 100
            results.append({
                'period': period,
                'actual_spend': actual,
                'growth': f"{growth:+.1f}%",
                'formula': f"(( {curr_val} - {prev_val} ) / {prev_val}) * 100"
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM/YoY)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    # Enforcement: Refuse if growth-type is not MoM or YoY (simulated)
    if args.growth_type not in ['MoM', 'YoY']:
        print("Error: --growth-type must be 'MoM' or 'YoY'.")
        return

    data = load_dataset(args.input)
    if not data:
        return

    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No data found for the specified ward and category.")
        return

    with open(args.output, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'actual_spend', 'growth', 'formula'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
