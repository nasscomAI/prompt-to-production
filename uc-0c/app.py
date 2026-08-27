import argparse
import csv
import sys
import os
from decimal import Decimal, ROUND_HALF_UP

def load_dataset(file_path):
    """
    Skill: load_dataset
    Description: reads CSV, validates columns, reports null count and which rows before returning.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    data = []
    required = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    null_rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not required.issubset(set(reader.fieldnames)):
                print(f"Error: Mandatory columns missing. Expected: {required}")
                sys.exit(1)
            
            for i, row in enumerate(reader, start=2):
                if not row['actual_spend'] or row['actual_spend'].strip() == "":
                    null_rows.append((i, row))
                data.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)

    # Reporting Requirement
    print(f"LOAD REPORT: {len(data)} rows loaded.")
    print(f"LOAD REPORT: Found {len(null_rows)} rows with null actual_spend.")
    for line, row in null_rows:
        print(f"  - [Line {line}] Ward: {row['ward']} | Category: {row['category']} | Period: {row['period']} | Reason: {row['notes']}")

    return data

def compute_growth(data, ward, category, growth_type):
    """
    Skill: compute_growth
    Description: takes ward + category + growth_type, returns per-period table with formula shown.
                 Must be a per-ward per-category table — not a single aggregated number.
    """
    # Enforcement: per-ward per-category filter (Prevents unauthorized aggregation)
    subset = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not subset:
        print(f"No records found for Ward: '{ward}' and Category: '{category}'.")
        return []

    subset.sort(key=lambda x: x['period'])

    results = []
    for i, row in enumerate(subset):
        period = row['period']
        spend_str = row['actual_spend']
        notes = row['notes']
        
        res = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': spend_str if spend_str else "NULL",
            'Growth': "N/A",
            'Formula': "N/A",
            'Note': notes if notes else "Computed"
        }

        # Null handling requirement
        if not spend_str:
            res['Growth'] = "NULL"
            res['Formula'] = "n/a"
            res['Note'] = f"FLAGGED: {notes}"
            results.append(res)
            continue

        curr_val = Decimal(spend_str)
        
        if growth_type == "MoM":
            if i > 0:
                prev_row = subset[i-1]
                prev_str = prev_row['actual_spend']
                if prev_str:
                    prev_val = Decimal(prev_str)
                    if prev_val != 0:
                        growth = (curr_val - prev_val) / prev_val
                        # Round to 1 decimal place for consistent display
                        growth_pct = (growth * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                        res['Growth'] = f"{growth_pct:+.1f}%"
                        res['Formula'] = f"({curr_val} - {prev_val}) / {prev_val}"
                    else:
                        res['Growth'] = "INF"
                        res['Formula'] = f"({curr_val} - 0) / 0"
                else:
                    res['Growth'] = "N/A"
                    res['Formula'] = f"({curr_val} - NULL) / NULL"
            else:
                res['Growth'] = "N/A (First)"
                res['Formula'] = "n/a"
        
        elif growth_type == "YoY":
            try:
                y, m = map(int, period.split('-'))
                prev_p = f"{y-1}-{m:02d}"
                prev_row = next((r for r in data if r['ward'] == ward and r['category'] == category and r['period'] == prev_p), None)
                if prev_row and prev_row['actual_spend']:
                    prev_val = Decimal(prev_row['actual_spend'])
                    growth = (curr_val - prev_val) / prev_val
                    growth_pct = (growth * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
                    res['Growth'] = f"{growth_pct:+.1f}%"
                    res['Formula'] = f"({curr_val} - {prev_val}) / {prev_val}"
                else:
                    res['Growth'] = "N/A"
                    res['Formula'] = "No prior year data"
            except:
                res['Growth'] = "Error"
                res['Formula'] = "Invalid period"
        
        results.append(res)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Analysis Tool — Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Specific ward name (Refusal if missing)")
    parser.add_argument("--category", help="Specific budget category (Refusal if missing)")
    parser.add_argument("--growth-type", help="Growth metric: MoM or YoY (Refusal if missing)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    parser.add_argument("--append", action="store_true", help="Append results to existing file if it exists")

    args = parser.parse_args()

    # Enforcement: Refusal Conditions
    if not args.growth_type:
        print("REFUSAL: --growth-type is mandatory. Refusing to guess between MoM or YoY.")
        sys.exit(1)
    
    if not args.ward or not args.category:
        print("REFUSAL: Specific --ward and --category are mandatory. Aggregation is forbidden per agents.md.")
        sys.exit(1)

    # Execute skills as defined in skills.md
    dataset = load_dataset(args.input)
    analysis = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if analysis:
        # Write to per-ward per-category table
        try:
            file_exists = os.path.exists(args.output)
            mode = 'a' if args.append and file_exists else 'w'
            
            with open(args.output, mode, newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=analysis[0].keys())
                if mode == 'w':
                    writer.writeheader()
                writer.writerows(analysis)
            
            action = "appended to" if mode == 'a' else "saved to"
            print(f"SUCCESS: Analysis results {action} '{args.output}'.")
        except Exception as e:
            print(f"Error: Could not save to {args.output} ({e})")
            sys.exit(1)

if __name__ == "__main__":
    main()
