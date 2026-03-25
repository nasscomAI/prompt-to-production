import argparse
import csv
import sys
import os

def load_dataset(file_path):
    """
    Reads the budget CSV file, validates columns, and reports null count 
    and the specific rows with null actual_spend values.
    """
    rows = []
    null_rows = []
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
        
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Validate columns
            required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
            fieldnames = reader.fieldnames or []
            if not all(col in fieldnames for col in required_cols):
                missing = [col for col in required_cols if col not in fieldnames]
                print(f"Error: Missing columns: {missing}")
                sys.exit(1)
                
            for i, row in enumerate(reader, start=2):
                if not row['actual_spend'] or row['actual_spend'].strip() == '':
                    null_rows.append((i, row))
                rows.append(row)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        sys.exit(1)
    
    # Report nulls as per skills.md
    if null_rows:
        print(f"NULL DETECTION REPORT: Found {len(null_rows)} null actual_spend values.")
        for line_num, row in null_rows:
            print(f"  - Ward: {row['ward']}, Category: {row['category']}, Period: {row['period']} (Line {line_num})")
            print(f"    Reason: {row['notes']}")
    else:
        print("No null actual_spend values found.")
        
    return rows

def compute_growth(dataset, ward_filter, category_filter, growth_type):
    """
    Calculates growth (e.g., MoM) for actual spend for a specific ward and category.
    Returns per-period table with formula shown.
    Refuses if aggregation is requested.
    """
    # Enforcement: If --growth-type is not specified — refuse and ask, never guess.
    if not growth_type:
        print("Error: --growth-type is not specified. Refusing to proceed. Please specify 'MoM'.")
        sys.exit(1)
        
    if growth_type != 'MoM':
        print(f"Error: Growth type '{growth_type}' is not supported. Use 'MoM'.")
        sys.exit(1)

    # Enforcement: Never aggregate across wards or categories.
    # If the filter is "All", we process each combination separately, NO SUMMING.
    
    # Filter and group data by (ward, category) to process every series independently
    series_map = {}
    for row in dataset:
        ward = row['ward']
        category = row['category']
        
        if (ward_filter == 'All' or ward == ward_filter) and \
           (category_filter == 'All' or category == category_filter):
            key = (ward, category)
            if key not in series_map:
                series_map[key] = []
            series_map[key].append(row)
            
    if not series_map:
        print(f"No data found for Ward: {ward_filter}, Category: {category_filter}")
        return []

    all_results = []
    
    # Process each (ward, category) series separately (NO aggregate SUMMING across series)
    for (ward, category), series in series_map.items():
        series.sort(key=lambda x: x['period'])
        prev_actual = None
        
        for row in series:
            period = row['period']
            actual_str = row['actual_spend']
            notes = row['notes']
            
            res = {
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': actual_str if actual_str else 'NULL',
                'growth': 'n/a',
                'formula': 'n/a'
            }
            
            if not actual_str:
                res['growth'] = 'FLAGGED'
                res['formula'] = f"NULL DATA: {notes}"
                all_results.append(res)
                prev_actual = None
                continue
                
            current_actual = float(actual_str)
            if prev_actual is not None:
                if prev_actual == 0:
                    res['growth'] = 'n/a'
                    res['formula'] = 'Previous spend was zero'
                else:
                    growth = ((current_actual - prev_actual) / prev_actual) * 100
                    res['growth'] = f"{growth:+.1f}%"
                    res['formula'] = f"(({current_actual} - {prev_actual}) / {prev_actual}) * 100"
            else:
                res['growth'] = 'n/a'
                res['formula'] = 'Baseline (First month or previous month was NULL)'
                
            all_results.append(res)
            prev_actual = current_actual
            
    # Final sort for clear output
    all_results.sort(key=lambda x: (x['ward'], x['category'], x['period']))
    return all_results

def main():
    parser = argparse.ArgumentParser(description="Budget Growth Analyst Agent")
    parser.add_argument('--input', help="Path to ward_budget.csv")
    parser.add_argument('--ward', help="Specific ward name or 'All'")
    parser.add_argument('--category', help="Specific category name or 'All'")
    parser.add_argument('--growth-type', help="Type of growth calculation (e.g., MoM)")
    parser.add_argument('--output', help="Output CSV path")
    
    args = parser.parse_args()
    
    # Explicitly check for growth-type as per agents.md rule
    if not args.growth_type:
        print("Error: --growth-type is not specified. Refusing to guess. Please provide --growth-type MoM.")
        sys.exit(1)

    if not args.input or not args.ward or not args.category or not args.output:
        print("Error: Missing required arguments. Usage: app.py --input <path> --ward <name> --category <name> --growth-type MoM --output <path>")
        sys.exit(1)

    print(f"Processing data for Ward: {args.ward}, Category: {args.category}...")
    dataset = load_dataset(args.input)
    
    # The compute_growth handles the "All" logic by processing series independently (no aggregation)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    
    if results:
        try:
            with open(args.output, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['period', 'ward', 'category', 'actual_spend', 'growth', 'formula'])
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully generated {args.output} with {len(results)} rows.")
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
