"""
UC-0C app.py — Deterministic Growth Configurator.
Enforces all UC-0C RICE rules from agents.md.
"""
import argparse
import csv
import sys

def load_dataset(input_path: str) -> list:
    data = []
    nulls = 0
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row['actual_spend'].strip():
                    nulls += 1
                data.append(row)
        print(f"Loaded {len(data)} rows. Found {nulls} nulls in actual_spend.")
        return data
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    if not ward or not category:
        print("REFUSED: Cannot aggregate across wards or categories.")
        sys.exit(1)
        
    if not growth_type:
        print("REFUSED: --growth-type not specified.")
        sys.exit(1)
        
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i in range(len(filtered)):
        row = filtered[i]
        period = row['period']
        spend_str = row['actual_spend'].strip()
        
        if not spend_str:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': 'NULL',
                'MoM Growth': f"FLAGGED: {row['notes']}"
            })
            continue
            
        spend = float(spend_str)
        if i == 0 or not filtered[i-1]['actual_spend'].strip():
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': spend,
                'MoM Growth': 'n/a (no reliable previous data)'
            })
            continue
            
        prev_spend = float(filtered[i-1]['actual_spend'].strip())
        
        if growth_type == 'MoM':
            if prev_spend == 0:
                 growth = 0
            else:
                 growth = ((spend - prev_spend) / prev_spend) * 100
            
            # Match the reference values: "+33.1%"
            sign = "+" if growth > 0 else "−" if growth < 0 else ""
            formula = f"({spend} - {prev_spend}) / {prev_spend}"
            # Format output specifically to reference
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': spend,
                'MoM Growth': f"{sign}{abs(growth):.1f}% [{formula}]"
            })
        else:
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': spend,
                'MoM Growth': f"Unsupported growth type: {growth_type}"
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    if args.ward is None or args.category is None:
        print("REFUSED: Aggregation across wards or categories without explicit instructions is forbidden.")
        sys.exit(1)
    if args.growth_type is None:
        print("REFUSED: Growth type requested unsupported or missing.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        # Strict mapping to the requested output format reference
        writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend', 'MoM Growth'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
