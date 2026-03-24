import argparse
import csv
import sys
import os

def load_dataset(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    return data

def compute_growth(data, ward, category, growth_type):
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError("Unknown growth-type. Must be MoM or YoY.")
        
    filtered = [row for row in data if row['ward'] == ward and row['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend = row['actual_spend']
        notes = row.get('notes', '')
        
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual_spend if actual_spend else 'NULL',
            'growth': 'NULL',
            'formula': '',
            'flag': ''
        }
        
        if not actual_spend or actual_spend.strip() == '':
            result_row['flag'] = f"NULL DATA: {notes}"
            results.append(result_row)
            continue
            
        current_val = float(actual_spend)
        
        if growth_type == "MoM":
            if i > 0:
                prev_row = filtered[i-1]
                prev_spend = prev_row['actual_spend']
                if prev_spend and prev_spend.strip() != '':
                    prev_val = float(prev_spend)
                    if prev_val == 0:
                        growth = 0.0
                    else:
                        growth = ((current_val - prev_val) / prev_val) * 100
                    
                    sign = "+" if growth > 0 else ""
                    result_row['growth'] = f"{sign}{growth:.1f}% ({notes})" if notes else f"{sign}{growth:.1f}%"
                    result_row['formula'] = f"({current_val} - {prev_val}) / {prev_val} * 100"
                else:
                    result_row['formula'] = "Previous period data is NULL"
            else:
                result_row['formula'] = "No previous period"
                
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Financial Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    if args.ward.lower() == 'all' or args.category.lower() == 'all':
        print("REFUSAL: Never aggregate across wards or categories.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    results = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if not results:
        print("No data found for the given ward and category.")
        sys.exit(1)
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'flag']
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Growth computation written to {args.output}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_input = os.path.join(base_dir, '..', 'data', 'budget', 'ward_budget.csv')
        sys.argv.extend([
            '--input', default_input,
            '--ward', 'Ward 1 – Kasba',
            '--category', 'Roads & Pothole Repair',
            '--growth-type', 'MoM',
            '--output', 'growth_output.csv'
        ])
    main()
