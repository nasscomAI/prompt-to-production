import argparse
import csv
import sys
import os

def load_dataset(filepath):
    """
    Skill 1: reads CSV, validates columns, reports null count.
    """
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit(1)
    data = []
    null_count = 0
    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required = {'period', 'ward', 'category', 'actual_spend', 'notes'}
            if not required.issubset(set(reader.fieldnames)):
                print("Error: Missing required columns in CSV.")
                sys.exit(1)
            for row in reader:
                val = row['actual_spend'].strip().upper()
                if not val or val == 'NULL':
                    null_count += 1
                data.append(row)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    print(f"Dataset loaded. Total rows: {len(data)}. Null actual_spend rows: {null_count}")
    return data

def compute_pair_growth(subset, ward, category):
    """
    Helper to compute growth for a single ward-category subset.
    Output structure matches README Reference Values.
    """
    subset.sort(key=lambda x: x['period'])
    results = []
    for i, row in enumerate(subset):
        period = row['period']
        actual_str = row['actual_spend'].strip()
        is_null = not actual_str or actual_str.upper() == 'NULL'
        
        output_row = {
            "Ward": ward,
            "Category": category,
            "Period": period,
            "Actual Spend (₹ lakh)": "NULL" if is_null else actual_str,
            "MoM Growth": ""
        }
        
        if is_null:
            # Match README Table: "Must be flagged — not computed"
            output_row["MoM Growth"] = "Must be flagged — not computed"
        elif i == 0:
            output_row["MoM Growth"] = "n/a"
        else:
            prev_row = subset[i-1]
            prev_actual_str = prev_row['actual_spend'].strip()
            prev_is_null = not prev_actual_str or prev_actual_str.upper() == 'NULL'
            
            if not prev_is_null:
                curr_val = float(actual_str)
                prev_val = float(prev_actual_str)
                if prev_val != 0:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    sign = "+" if growth >= 0 else "−"
                    growth_val_str = f"{sign}{abs(growth):.1f}%"
                    
                    # Match README Table: Suffix notes if present
                    note = row['notes'].strip()
                    if note:
                        output_row["MoM Growth"] = f"{growth_val_str} ({note})"
                    else:
                        output_row["MoM Growth"] = growth_val_str
                else:
                    output_row["MoM Growth"] = "n/a (Prev is 0)"
            else:
                output_row["MoM Growth"] = "n/a (Prev value is NULL)"
        results.append(output_row)
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    if not args.growth_type:
        print("Refusal: --growth-type not specified. Refusing to guess formula.")
        sys.exit(1)
        
    data = load_dataset(args.input)
    
    # Identify unique pairs to process
    if args.ward and args.category:
        pairs = [(args.ward, args.category)]
    else:
        # All-ward/category batch processing (Granular, no aggregation)
        pairs = sorted(list(set((r['ward'], r['category']) for r in data)))
    
    all_results = []
    for w, c in pairs:
        subset = [r for r in data if r['ward'] == w and r['category'] == c]
        if subset:
            all_results.extend(compute_pair_growth(subset, w, c))
            
    if all_results:
        try:
            with open(args.output, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["Ward", "Category", "Period", "Actual Spend (₹ lakh)", "MoM Growth"])
                writer.writeheader()
                writer.writerows(all_results)
            print(f"Success: Results written to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()