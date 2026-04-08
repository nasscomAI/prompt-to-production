import argparse
import csv
import sys

def load_dataset(file_path):
    """Reads CSV, validates columns, reports null count and reasons."""
    required_cols = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    data = []
    null_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Column validation
            headers = set(reader.fieldnames or [])
            if not required_cols.issubset(headers):
                raise ValueError(f"Missing required columns. Found: {headers}")

            for row_idx, row in enumerate(reader, start=2):
                actual = row.get('actual_spend', '').strip()
                if not actual:
                    null_count += 1  # type: ignore
                    reason = row.get('notes', 'No reason provided')
                    print(f"FLAG: Null 'actual_spend' detected on row {row_idx} | "
                          f"Ward: {row['ward']} | Category: {row['category']} | "
                          f"Period: {row['period']} | Reason: '{reason}'")
                data.append(row)
                
    except FileNotFoundError:
        print(f"Error: Dataset not found at {file_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"\nDataset loaded. Found {null_count} null actual_spend rows.")
    return data

def compute_growth(data, ward, category, growth_type):
    """Computes per-period table with formula shown."""
    # Enforcement: Refuse missing growth-type
    if not growth_type:
        print("Error: --growth-type must be specified. System refuses to guess (e.g., MoM or YoY).", file=sys.stderr)
        sys.exit(1)
        
    # Enforcement: Refuse overall aggregations
    if not ward or ward.lower() == 'all':
        print("Error: Aggregation across multiple wards is explicitly prohibited. Please specify a single ward.", file=sys.stderr)
        sys.exit(1)
    if not category or category.lower() == 'all':
        print("Error: Aggregation across multiple categories is explicitly prohibited. Please specify a single category.", file=sys.stderr)
        sys.exit(1)

    # Filter data
    filtered_data = [row for row in data if row['ward'] == ward and row['category'] == category]
    
    if not filtered_data:
        print(f"Warning: No data found for Ward: '{ward}' and Category: '{category}'")
        return []

    # Sort chronologically
    filtered_data.sort(key=lambda x: x['period'])

    results = []
    
    for i in range(len(filtered_data)):
        current_row = filtered_data[i]
        period = current_row['period']
        current_actual = current_row.get('actual_spend', '').strip()
        
        growth_key = f'{growth_type} Growth'
        output_row = {
            'Ward': ward,
            'Category': category,
            'Period': period,
            'Actual Spend (₹ lakh)': current_actual if current_actual else 'NULL',
            growth_key: '',
            'Formula': ''
        }

        # Handling null current month
        if not current_actual:
            output_row[growth_key] = 'FLAGGED_NULL'
            output_row['Formula'] = f"Not computed due to NULL actual_spend: {current_row.get('notes', '')}"
            results.append(output_row)
            continue
            
        current_val = float(current_actual)

        # compute growth based on type
        if growth_type.upper() == 'MOM':
            if i == 0:
                output_row[growth_key] = 'N/A (First Month)'
                output_row['Formula'] = 'n/a'
            else:
                prev_row = filtered_data[i-1]
                prev_actual = prev_row.get('actual_spend', '').strip()
                
                if not prev_actual:
                    output_row[growth_key] = 'N/A (Prev Month NULL)'
                    output_row['Formula'] = 'n/a'
                else:
                    prev_val = float(prev_actual)
                    if prev_val == 0:
                        output_row[growth_key] = 'Undefined (Div by 0)'
                        output_row['Formula'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
                    else:
                        growth = ((current_val - prev_val) / prev_val) * 100
                        output_row[growth_key] = f"{growth:+.1f}%"
                        output_row['Formula'] = f"(({current_val} - {prev_val}) / {prev_val}) * 100"
                        
        else:
            print(f"Error: Unsupported growth type '{growth_type}'", file=sys.stderr)
            sys.exit(1)
            
        results.append(output_row)

    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    
    # We don't mark these as required by argparse because we want our business logic to refuse it explicitly 
    # instead of a generic argparse error.
    parser.add_argument("--ward", help="Target ward for analysis")
    parser.add_argument("--category", help="Target category for analysis")
    parser.add_argument("--growth-type", help="Type of growth calculation (e.g., MoM)")

    args = parser.parse_args()

    # Skill 1: load dataset
    print(f"Loading data from {args.input}...")
    dataset = load_dataset(args.input)

    # Skill 2: compute growth
    print(f"Computing {args.growth_type} growth for Ward: '{args.ward}', Category: '{args.category}'...")
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    if not results:
        print("No results to write. Exiting.")
        sys.exit(0)

    # Output to CSV
    print(f"Writing {len(results)} rows to {args.output}...")
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Ward', 'Category', 'Period', 'Actual Spend (₹ lakh)', f'{args.growth_type} Growth', 'Formula']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print("Done.")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
