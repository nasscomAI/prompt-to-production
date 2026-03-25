import pandas as pd
import argparse
 
def load_dataset(path):
    df = pd.read_csv(path)
 
    required_cols = [
        "period", "ward", "category",
        "budgeted_amount", "actual_spend", "notes"
    ]
 
    for col in required_cols:
        if col not in df.columns:
            raise Exception(f"Missing column: {col}")
 
    null_rows = df[df["actual_spend"].isnull()]
 
    if not null_rows.empty:
        print("⚠ Null rows detected:")
        print(null_rows[["period", "ward", "category", "notes"]])
 
    return df
 
 
def compute_growth(df, ward, category, growth_type):
    if growth_type is None:
        raise Exception("❌ growth-type must be specified")
 
    df = df[(df["ward"] == ward) & (df["category"] == category)] # Filter by ward and category
 
    df = df.sort_values("period")
 
    results = []
 
    prev_value = None
 
    for _, row in df.iterrows():
        current = row["actual_spend"]
 
        if pd.isnull(current):
            results.append({
                "period": row["period"],
                "growth": "NULL",
                "formula": "Skipped due to NULL"
            })
            prev_value = None
            continue
 
        if prev_value is None:
            growth = "NA"
            formula = "No previous value"
        else:
            growth_val = ((current - prev_value) / prev_value) * 100
            growth = f"{growth_val:.2f}%"
            formula = f"(({current} - {prev_value}) / {prev_value}) * 100"
 
        results.append({
            "period": row["period"],
            "growth": growth,
            "formula": formula
        })
 
        prev_value = current
 
    return pd.DataFrame(results)
 
 
def main():
    parser = argparse.ArgumentParser()
 
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
 
    args = parser.parse_args()
 
    df = load_dataset(args.input)
 
    result = compute_growth(
        df,
        args.ward,
        args.category,
        args.growth_type
    )
 
    result.to_csv(args.output, index=False)
    print("✅ Output saved:", args.output)
 
 
if __name__ == "__main__":
    main()