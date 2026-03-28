"""
UC-0C app.py
Rule-based heuristic implementation based strictly on agents.md enforcement rules.
"""
import argparse
import csv

def main(input_path: str, ward: str, category: str, growth_type: str, output_path: str):
    # Rule 4: If growth_type not specified or empty — refuse and ask
    if not growth_type:
        print("Error: --growth-type must be specified.")
        return
        
    # Rule 1: Never aggregate across wards or categories unless explicitly instructed
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        print("Refusal: Aggregation across multiple wards or categories is not permitted.")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    # Filter
    filtered = [r for r in rows if r.get('ward') == ward and r.get('category') == category]
    
    out_rows = []
    
    for i in range(len(filtered)):
        row = filtered[i]
        period = row.get('period', '')
        actual = row.get('actual_spend', '').strip()
        notes = row.get('notes', '')
        
        # Rule 2: Flag every null row before computing — report reason
        if not actual:
            out_rows.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': f"MUST BE FLAGGED - null reason: {notes}",
                'formula': 'N/A'
            })
            continue
            
        growth = "n/a"
        formula = "n/a"
        
        # Determine previous actual_spend handling null rows safely
        prev_actual = None
        if i > 0:
            prev_row = filtered[i-1]
            p_actual = prev_row.get('actual_spend', '').strip()
            if p_actual:
                prev_actual = float(p_actual)
                
        if prev_actual is not None and actual:
            try:
                curr = float(actual)
                growth_val = ((curr - prev_actual) / prev_actual) * 100
                growth = f"{growth_val:+.1f}%"
                formula = f"(({curr} - {prev_actual}) / {prev_actual}) * 100"
            except ValueError:
                pass
                
        out_rows.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual,
            'growth': growth,
            'formula': formula
        })
        
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth', 'formula'])
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Computed dataset exported to {output_path}")
    except Exception as e:
        print(f"Failed to save output: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", dest="growth_type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.input, args.ward, args.category, args.growth_type, args.output)
