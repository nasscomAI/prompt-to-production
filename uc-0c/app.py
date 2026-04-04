import argparse
import csv
import sys

def load_dataset(input_path: str):
    print("Skill: load_dataset running...")
    rows = []
    null_count = 0
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            if not required_cols.issubset(set(reader.fieldnames)):
                print("SYSTEM ERROR: Dataset missing required granular columns.")
                sys.exit(1)
                
            for row in reader:
                if not row['actual_spend'].strip():
                    null_count += 1
                    print(f"FLAGGED HIGH RISK [NULL DETECTION]: Row {row['period']} | {row['ward']} | {row['category']} -> REASON: {row['notes']}")
                rows.append(row)
                
        print(f"Dataset securely loaded. Total records: {len(rows)}. Deliberate null holes verified: {null_count}.\n")
        return rows
    except Exception as e:
        print(f"SYSTEM ERROR reading dataset: {e}")
        sys.exit(1)

def compute_growth(rows, ward, category, growth_type):
    print("Skill: compute_growth running...")
    
    # 1. Enforcement restriction on aggregation assumption
    if not ward or ward.lower() == "any" or not category or category.lower() == "any":
        print("SYSTEM REFUSAL: Never aggregate across wards or categories collectively. Parameter specific filtering demanded.")
        sys.exit(1)
        
    filtered = [r for r in rows if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period']) # safely order time-series
    
    if growth_type.upper() == 'MOM':
        results = []
        for i in range(len(filtered)):
            curr = filtered[i]
            spend_str = curr['actual_spend'].strip()
            
            # 2. Enforcement Null Handling (DO NOT Compute, Explicit flag + note propagation)
            if not spend_str:
                results.append({
                    'ward': ward, 'category': category, 'period': curr['period'],
                    'actual_spend': 'NULL',
                    'growth': f"Must be flagged — not computed (Reason: {curr['notes']})"
                })
                continue
                
            current_spend = float(spend_str)
            if i == 0:
                results.append({
                    'ward': ward, 'category': category, 'period': curr['period'],
                    'actual_spend': current_spend, 'growth': "n/a (First evaluated period)"
                })
                continue
                
            prev = filtered[i-1]
            prev_spend_str = prev['actual_spend'].strip()
            if not prev_spend_str:
                results.append({
                    'ward': ward, 'category': category, 'period': curr['period'],
                    'actual_spend': current_spend, 'growth': "n/a (Previous block was NULL)"
                })
                continue
                
            prev_spend = float(prev_spend_str)
            if prev_spend == 0:
                growth_str = "n/a (Denominator Zero)"
            else:
                pct = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if pct > 0 else ""
                note = f" ({curr['notes']})" if curr.get('notes') and curr['notes'].strip() else ""
                # 3. Enforcement Formula Transparency
                formula_str = f"[Formula: (({current_spend} - {prev_spend}) / {prev_spend}) * 100]"
                growth_str = f"{sign}{pct:.1f}%{note} {formula_str}"
                
            results.append({
                'ward': ward, 'category': category, 'period': curr['period'],
                'actual_spend': current_spend, 'growth': growth_str
            })
            
        return results
    else:
        print(f"SYSTEM REFUSAL: Invalid analytic method '{growth_type}'.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Agent Worker")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--growth-type", default=None)
    parser.add_argument("--output", required=True)
    
    args = parser.parse_args()
    
    # 4. Enforcement restriction on Interval Defaulting
    if not args.growth_type:
        print("SYSTEM REFUSAL: `--growth-type` command parameter not specified. Implicit default assumptions (e.g. MoM or YoY) are prohibited. Please supply explicitly.")
        sys.exit(1)
        
    dataset = load_dataset(args.input)
    growth_results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ward', 'category', 'period', 'actual_spend', 'growth'])
        writer.writeheader()
        writer.writerows(growth_results)
        
    print(f"\nOperations complete. Deterministic computation tracking output safely saved to: {args.output}")

if __name__ == "__main__":
    main()
