"""
UC-0C app.py
Growth calculation with explicit anti-hallucination and refusal checks.
"""
import argparse
import csv
import sys

def load_dataset(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"Error reading dataset: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Validate and report nulls
    null_rows = []
    for row in data:
        if not row.get('actual_spend') or str(row['actual_spend']).strip() == '' or str(row['actual_spend']).strip().lower() == 'null':
            null_rows.append(row)
            
    if null_rows:
        print(f"Flagging {len(null_rows)} null actual_spend rows:", file=sys.stderr)
        for r in null_rows:
            # We must report the null reason from the notes column
            notes = r.get('notes', '').strip()
            if not notes:
                notes = "No reason provided"
            print(f" - {r.get('ward', 'Unknown')} | {r.get('category', 'Unknown')} | {r.get('period', 'Unknown')}: {notes}", file=sys.stderr)
            
    return data

def compute_growth(data, ward, category, growth_type):
    # Rule: Never aggregate across wards or categories unless explicitly instructed — refuse if asked
    if not ward or str(ward).strip().lower() == 'any':
        raise ValueError("Refusal: Never aggregate across wards unless explicitly instructed.")
    if not category or str(category).strip().lower() == 'any':
        raise ValueError("Refusal: Never aggregate across categories unless explicitly instructed.")
        
    # Rule: If --growth-type not specified — refuse and ask, never guess
    if not growth_type:
        raise ValueError("Refusal: --growth-type not specified. Cannot guess the growth type.")
        
    filtered = [d for d in data if d.get('ward') == ward and d.get('category') == category]
    
    if not filtered:
        print(f"Warning: No data found for ward '{ward}' and category '{category}'.", file=sys.stderr)
        return []
        
    # Ensure data is sorted chronologically
    filtered.sort(key=lambda x: x.get('period', ''))
    
    results = []
    for i in range(len(filtered)):
        row = filtered[i]
        period = row.get('period', '')
        current_spend_str = str(row.get('actual_spend', '')).strip()
        if current_spend_str.lower() == 'null':
            current_spend_str = ''
            
        result_row = {
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': current_spend_str if current_spend_str else 'NULL',
            'growth': 'NULL',
            'formula': 'NULL',
            'notes': row.get('notes', '').strip()
        }
        
        if not current_spend_str:
            result_row['notes'] = "Null actual spend. " + result_row['notes']
            result_row['notes'] = result_row['notes'].strip()
            results.append(result_row)
            continue
            
        try:
            current_spend = float(current_spend_str)
        except ValueError:
            result_row['notes'] = "Invalid spend value. " + result_row['notes']
            results.append(result_row)
            continue
            
        if growth_type.upper() == 'MOM':
            if i == 0:
                result_row['formula'] = 'n/a (first period)'
            else:
                prev_row = filtered[i-1]
                prev_spend_str = str(prev_row.get('actual_spend', '')).strip()
                if prev_spend_str.lower() == 'null':
                    prev_spend_str = ''
                    
                if not prev_spend_str:
                    result_row['formula'] = 'n/a (previous period is null)'
                else:
                    try:
                        prev_spend = float(prev_spend_str)
                        if prev_spend == 0:
                            result_row['formula'] = 'n/a (division by zero)'
                        else:
                            growth_val = (current_spend - prev_spend) / prev_spend * 100
                            result_row['growth'] = f"{growth_val:+.1f}%"
                            result_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                    except ValueError:
                        result_row['formula'] = 'n/a (invalid previous period value)'
        elif growth_type.upper() == 'YOY':
            try:
                year, month = period.split('-')
                prev_period = f"{int(year)-1}-{month}"
            except ValueError:
                result_row['formula'] = 'n/a (invalid period format)'
                results.append(result_row)
                continue
                
            prev_row = next((r for r in filtered if r.get('period') == prev_period), None)
            
            if not prev_row:
                 result_row['formula'] = 'n/a (no data for previous year)'
            else:
                prev_spend_str = str(prev_row.get('actual_spend', '')).strip()
                if prev_spend_str.lower() == 'null':
                    prev_spend_str = ''
                    
                if not prev_spend_str:
                    result_row['formula'] = 'n/a (previous year is null)'
                else:
                    try:
                        prev_spend = float(prev_spend_str)
                        if prev_spend == 0:
                            result_row['formula'] = 'n/a (division by zero)'
                        else:
                            growth_val = (current_spend - prev_spend) / prev_spend * 100
                            result_row['growth'] = f"{growth_val:+.1f}%"
                            result_row['formula'] = f"({current_spend} - {prev_spend}) / {prev_spend} * 100"
                    except ValueError:
                        result_row['formula'] = 'n/a (invalid previous year value)'
        else:
             raise ValueError(f"Refusal: Unknown growth type '{growth_type}'.")
             
        results.append(result_row)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Calculate growth for a specific ward and category.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--ward", help="Ward name (must not be 'Any')")
    parser.add_argument("--category", help="Category name (must not be 'Any')")
    parser.add_argument("--growth-type", help="Type of growth to compute (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Cannot guess the growth type.", file=sys.stderr)
        sys.exit(1)
        
    if not args.ward or args.ward.strip().lower() == 'any' or not args.category or args.category.strip().lower() == 'any':
        print("Refusal: Never aggregate across wards or categories unless explicitly instructed.", file=sys.stderr)
        sys.exit(1)
        
    data = load_dataset(args.input)
    
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
        
    if not results:
        print("No results to write.", file=sys.stderr)
        sys.exit(0)
        
    fieldnames = ['period', 'ward', 'category', 'actual_spend', 'growth', 'formula', 'notes']
    try:
        with open(args.output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully wrote output to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
