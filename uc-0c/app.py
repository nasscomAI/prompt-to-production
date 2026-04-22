import argparse
import pandas as pd
import sys

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Reads the budget CSV file, validates columns, and reports null count and which rows have missing values.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read file {file_path}. {e}")
        sys.exit(1)
        
    required_columns = ['ward', 'category', 'period', 'actual_spend', 'notes']
    for col in required_columns:
        if col not in df.columns:
            print(f"Error: Missing required column: {col}")
            sys.exit(1)
            
    # Flag every null row before computing
    null_rows = df[df['actual_spend'].isnull()]
    if not null_rows.empty:
        print("--- Pre-computation Null Report ---")
        print(f"Total null actual_spend rows: {len(null_rows)}")
        for index, row in null_rows.iterrows():
            ward = row.get('ward', 'Unknown')
            period = row.get('period', 'Unknown')
            category = row.get('category', 'Unknown')
            reason = row.get('notes', 'No reason provided')
            print(f"Row {index} (Ward: {ward}, Category: {category}, Period: {period}) - Null Reason: {reason}")
        print("-----------------------------------\n")
        
    return df

def compute_growth(df: pd.DataFrame, ward: str, category: str, growth_type: str) -> list:
    """
    Computes financial growth metrics per-period for a specific ward and category.
    Returns a list of results for each period.
    """
    if not growth_type:
        print("Error: --growth-type not specified. Please provide a growth type (e.g., MoM, YoY). I cannot guess this for you.")
        sys.exit(1)
        
    if not ward or not category:
        print("Error: Aggregation across wards or categories is not allowed. Please explicitly specify both --ward and --category.")
        sys.exit(1)
        
    filtered_df = df[(df['ward'] == ward) & (df['category'] == category)].copy()
    
    if filtered_df.empty:
        print(f"No data found for Ward: {ward}, Category: {category}")
        return []
        
    # Assuming period can be sorted logically
    filtered_df = filtered_df.sort_values(by='period')
    
    print(f"--- Growth Report: Ward {ward}, Category {category} ---")
    print(f"Growth Type: {growth_type}")
    print("-" * 60)
    
    previous_spend = None
    results = []
    
    for index, row in filtered_df.iterrows():
        period = row['period']
        actual_spend = row['actual_spend']
        
        if pd.isnull(actual_spend):
            growth_str = "N/A"
            formula = "N/A (Null value)"
            print(f"Period: {period} | Spend: Null | Growth: {growth_str} | Formula: {formula}")
        elif previous_spend is None:
            growth_str = "N/A"
            formula = "First valid period"
            print(f"Period: {period} | Spend: {actual_spend} | Growth: {growth_str} | Formula: {formula} (No previous data to compare)")
        else:
            if previous_spend == 0:
                growth_str = "Infinity"
                formula = f"({actual_spend} - {previous_spend}) / {previous_spend} (Div by Zero)"
            else:
                growth = (actual_spend - previous_spend) / previous_spend * 100
                growth_str = f"{growth:.2f}%"
                formula = f"({actual_spend} - {previous_spend}) / {previous_spend} * 100"
            print(f"Period: {period} | Spend: {actual_spend} | Growth: {growth_str} | Formula: {formula}")
            
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': actual_spend,
            'growth': growth_str,
            'formula': formula
        })
            
        if not pd.isnull(actual_spend):
            previous_spend = actual_spend
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Budget Analysis Agent")
    parser.add_argument("--input", "--file", dest="file", default="ward_budget.csv", help="Path to the budget CSV file")
    parser.add_argument("--ward", help="Specific ward to analyze (required to prevent aggregation)")
    parser.add_argument("--category", help="Specific category to analyze (required to prevent aggregation)")
    parser.add_argument("--growth-type", help="Type of growth to compute (e.g., MoM, YoY) (required)")
    parser.add_argument("--output", help="Path to save the output CSV")
    
    # We parse manually to handle missing args gracefully according to the prompt
    args, unknown = parser.parse_known_args()
    
    if not args.growth_type:
        print("Error: --growth-type not specified. Please specify it (e.g., --growth-type MoM).")
        sys.exit(1)
        
    if not args.ward or not args.category:
        print("Error: I am forbidden from aggregating across wards or categories unless explicitly instructed. Please provide both --ward and --category.")
        sys.exit(1)
    
    df = load_dataset(args.file)
    results = compute_growth(df, args.ward, args.category, args.growth_type)
    
    if args.output and results:
        try:
            output_df = pd.DataFrame(results)
            output_df.to_csv(args.output, index=False)
            print(f"\nSuccess: Results saved to {args.output}")
        except Exception as e:
            print(f"Error: Could not save results to {args.output}. {e}")

if __name__ == "__main__":
    main()
