import argparse
import csv

def compute_growth(input_path, ward, category, growth_type, output_path):
    if not ward or not category:
        print("REFUSED: Never aggregate across wards or categories unless explicitly instructed.")
        return

    if not growth_type:
        print("REFUSED: --growth-type not specified. Never guess.")
        return

    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['ward'] == ward and r['category'] == category:
                rows.append(r)
                
    rows.sort(key=lambda x: x['period'])
    
    results = []
    prev_val = None
    
    for row in rows:
        spend_str = row['actual_spend'].strip()
        notes = row.get('notes', '')
        
        flag = ""
        spend = None
        if not spend_str or spend_str.lower() == 'null':
            flag = "NULL_ACTUAL_SPEND"
            growth = "NULL"
            formula = "n/a"
            prev_val = None
        else:
            spend = float(spend_str)
            if prev_val is None:
                growth = "n/a"
                formula = "n/a"
            else:
                g = (spend - prev_val) / prev_val
                growth = f"{g:+.1%}"
                formula = f"({spend} - {prev_val}) / {prev_val}"
            prev_val = spend
            
        res_row = {
            'period': row['period'],
            'ward': ward,
            'category': category,
            'actual_spend': spend_str,
            'growth': growth,
            'formula': formula,
            'flag': flag,
            'notes': notes
        }
        results.append(res_row)
        
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'flag', 'notes'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    compute_growth(args.input, args.ward, args.category, args.growth_type, args.output)
