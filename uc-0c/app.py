"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
import os

def load_dataset(filepath: str) -> list:
    """Reads CSV, validates columns, reports null count and which rows before returning."""
    data = []
    null_rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("actual_spend") or row.get("actual_spend").strip() == "":
                null_rows.append(row)
            data.append(row)
            
    if null_rows:
        print(f"Warning: Found {len(null_rows)} deliberate null actual_spend values.")
        for r in null_rows:
            print(f"  - {r['period']} · {r['ward']} · {r['category']} (Notes: {r.get('notes', 'None')})")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """Takes ward + category + growth_type, returns per-period table with formula shown."""
    # Filter data
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row.get('notes', '')
        
        actual_val = None
        if actual_str:
            try:
                actual_val = float(actual_str)
            except ValueError:
                pass
                
        if actual_val is None:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend (₹ lakh)': 'NULL',
                'Growth': 'Must be flagged — not computed',
                'Formula': 'N/A',
                'Notes': notes
            })
            continue
            
        growth = "n/a"
        formula = "N/A"
        
        if growth_type.lower() == 'mom':
            if i > 0:
                prev_row = filtered[i-1]
                prev_actual_str = prev_row['actual_spend'].strip()
                if prev_actual_str:
                    try:
                        prev_val = float(prev_actual_str)
                        if prev_val != 0:
                            pct = ((actual_val - prev_val) / prev_val) * 100
                            sign = "+" if pct > 0 else ("−" if pct < 0 else "")
                            growth = f"{sign}{abs(pct):.1f}%"
                            formula = f"({actual_val} - {prev_val}) / {prev_val} * 100"
                    except ValueError:
                        pass
        elif growth_type.lower() == 'yoy':
            # Simplified YoY for the example, assumes data is exactly 1 year or matched by month
            # Since data is 12 months (Jan-Dec 2024), YoY isn't fully computable without 2023, but we add logic placeholder.
            pass
            
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': actual_val,
            'Growth': growth,
            'Formula': formula,
            'Notes': notes
        })
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", required=False, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=False, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, help="Growth type (e.g. 'MoM' or 'YoY')")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    if not args.ward or not args.category:
        print("Error: Must specify both --ward and --category. Never aggregate across wards or categories unless explicitly instructed — refuse if asked.")
        sys.exit(1)
        
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusing to guess. Please specify 'MoM' or 'YoY'.")
        sys.exit(1)
        
    if not os.path.exists(args.input):
        print(f"Error: File not found at {args.input}")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No data found for the specified ward and category.")
        sys.exit(0)
        
    fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', 'Growth', 'Formula', 'Notes']
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
