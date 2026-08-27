import pandas as pd
import argparse

def load_dataset(input_file):
    df = pd.read_csv(input_file)
    required_cols = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    return df

def compute_growth(df, ward, category, growth_type):
    df_filtered = df[(df['ward'] == ward) & (df['category'] == category)].sort_values('period')
    output_rows = []
    prev_actual = None

    for idx, row in df_filtered.iterrows():
        period = row['period']
        actual = row['actual_spend']
        formula = 'n/a'
        growth = 'n/a'

        # Handle null actual spend
        if pd.isna(actual):
            note = row.get('notes', 'NULL actual_spend')
            output_rows.append({
                'period': period,
                'ward': ward,
                'category': category,
                'actual_spend': 'NULL',
                'growth': 'n/a',
                'formula': 'n/a',
                'note': note
            })
            prev_actual = None
            continue

        # Compute MoM growth
        if prev_actual is not None:
            growth_val = (actual - prev_actual) / prev_actual * 100
            growth = f"{growth_val:+.1f}%"
            formula = f"({actual} - {prev_actual}) / {prev_actual}"
        output_rows.append({
            'period': period,
            'ward': ward,
            'category': category,
            'actual_spend': actual,
            'growth': growth,
            'formula': formula,
            'note': ''
        })
        prev_actual = actual

    return pd.DataFrame(output_rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--ward', required=True)
    parser.add_argument('--category', required=True)
    parser.add_argument('--growth-type', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    if args.growth_type not in ['MoM', 'YoY']:
        raise ValueError("Must specify growth-type as MoM or YoY")

    df = load_dataset(args.input)
    result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    result_df.to_csv(args.output, index=False)
    print(f"Output saved to {args.output}")

if __name__ == '__main__':
    main()