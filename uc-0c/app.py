import argparse
import pandas as pd
import sys

def load_dataset(file_path):
    print(f"Loading dataset from: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)
        
    required_columns = {'period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes'}
    if not required_columns.issubset(set(df.columns)):
        print(f"Error: Missing needed columns. Found {list(df.columns)}")
        sys.exit(1)
        
    null_rows = df[df['actual_spend'].isnull()]
    print(f"Validation Report: Found {len(null_rows)} null values in actual_spend.")
    for idx, row in null_rows.iterrows():
        print(f" - Null Flag: Row {idx} ({row['period']} | {row['ward']} | {row['category']}) -> Reason: {row['notes']}")

    return df

def compute_growth(df, ward, category, growth_type):
    # Ensure no cross-ward or cross-category aggregation
    if not ward or ward.lower() == 'any' or not category or category.lower() == 'any':
        print("Error: System MUST REFUSE all-ward/all-category aggregation. Please specify exact ward and category.")
        sys.exit(1)
        
    filtered = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered.empty:
        print(f"Warning: No matching data for Ward '{ward}' and Category '{category}'.")
        return filtered

    filtered = filtered.sort_values(by='period').reset_index(drop=True)
    
    if growth_type == 'MoM':
        # Previous month actual_spend
        prev_spend = filtered['actual_spend'].shift(1)
        
        growths = []
        formulas = []
        for idx, row in filtered.iterrows():
            current = row['actual_spend']
            prev = prev_spend[idx]
            
            if pd.isna(current):
                growths.append(None)
                formulas.append("NULL (Must be flagged - not computed)")
            elif pd.isna(prev):
                growths.append(None)
                formulas.append("N/A (No previous period)")
            elif prev == 0:
                growths.append(None)
                formulas.append("N/A (Previous period is zero)")
            else:
                growth_val = ((current - prev) / prev) * 100
                growths.append(f"{growth_val:+.1f}%")
                formulas.append(f"({current} - {prev}) / {prev} * 100")
                
        filtered['growth'] = growths
        filtered['formula'] = formulas
        return filtered

    else:
        print(f"Error: Growth type '{growth_type}' is not supported yet.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Calculate ward budget growth")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--ward', required=False, help="Ward name", default=None)
    parser.add_argument('--category', required=False, help="Category name", default=None)
    parser.add_argument('--growth-type', required=False, dest="growth_type", help="Type of growth calculation (e.g. MoM)", default=None)
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    args, unknown = parser.parse_known_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Refusal enforced. Please specify explicitly (e.g. MoM).")
        sys.exit(1)

    if not args.ward or not args.category or args.ward.lower() == 'any' or args.category.lower() == 'any':
        print("Error: Never aggregate across wards or categories. Exact --ward and --category must be specified.")
        sys.exit(1)

    df = load_dataset(args.input)
    
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    
    result_df.to_csv(args.output, index=False)
    print(f"Output saved successfully to {args.output}")

if __name__ == '__main__':
    main()
