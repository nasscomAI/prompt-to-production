import argparse
import csv
import os

def load_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        raise ValueError("Growth type not specified.")
    if ward == "Any" or category == "Any":
        raise ValueError("Aggregation across wards or categories is not allowed.")
    
    # Filter data
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    # Sort by period just in case
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual_str = row['actual_spend'].strip()
        notes = row.get('notes', '')
        
        if not actual_str or actual_str.lower() in ('null', 'none', ''):
            results.append({
                'Ward': ward,
                'Category': category,
                'Period': period,
                'Actual Spend': 'NULL',
                'Growth': f'Flagged: {notes}',
                'Formula': 'N/A (Missing Data)'
            })
            prev_spend = None
            continue
            
        actual = float(actual_str)
        
        if prev_spend is None:
            growth = "n/a"
            formula = "Base Month"
        else:
            if growth_type.upper() == 'MOM':
                growth_val = ((actual - prev_spend) / prev_spend) * 100
                growth = f"{growth_val:+.1f}%"
                formula = "(Current - Previous) / Previous"
            else:
                growth = "N/A"
                formula = "Unknown Growth Type"
                
        results.append({
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend': actual,
            'Growth': growth,
            'Formula': formula
        })
        prev_spend = actual
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = load_dataset(args.input)
    
    # Simulated AI logic handled via deterministic function for assignment tests
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(f"Error computing growth: {e}")
        return

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Ward', 'Category', 'Period', 'Actual Spend', 'Growth', 'Formula'])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
