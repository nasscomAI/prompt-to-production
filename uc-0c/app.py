import pandas as pd
import os

def analyze_budget(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    df.columns = [c.strip().lower() for c in df.columns]

    # 1. Get the unique periods (e.g., 'Current Year', 'Previous Year')
    periods = df['period'].unique().tolist()
    print(f"Found periods: {periods}")

    if len(periods) < 2:
        print(f"❌ Error: Need at least 2 unique periods in the 'period' column. Found: {periods}")
        return

    # Assuming the data is structured so the last one is 'Current' 
    # and the one before it is 'Previous'
    prev_period, curr_period = periods[0], periods[1] 
    print(f"Comparing {prev_period} (Prev) to {curr_period} (Curr)")

    # 2. Pivot the data
    pivot_df = df.pivot_table(
        index=['ward', 'category'], 
        columns='period', 
        values='budgeted_amount'
    ).reset_index()

    # 3. Calculate Growth using the exact names found in the CSV
    pivot_df['growth_percentage'] = ((pivot_df[curr_period] - pivot_df[prev_period]) / pivot_df[prev_period]) * 100
    pivot_df['growth_percentage'] = pivot_df['growth_percentage'].fillna(0)

    # 4. Apply Flag
    pivot_df['status'] = pivot_df['growth_percentage'].apply(lambda x: 'HIGH_GROWTH' if x > 20 else 'NORMAL')

    # 5. Save
    pivot_df.to_csv(output_file, index=False)
    print(f"✅ Success! Generated {output_file}")

if __name__ == "__main__":
    input_path = "../data/budget/ward_budget.csv"
    output_path = "growth_output.csv"
    analyze_budget(input_path, output_path)