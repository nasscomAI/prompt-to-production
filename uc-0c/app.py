import argparse
import pandas as pd

REQUIRED_COLUMNS = [
    "period","ward","category","budgeted_amount","actual_spend","notes"
]

def load_dataset(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print("NULL rows detected:")
        print(null_rows[["period","ward","category","notes"]].to_string(index=False))
    return df

def compute_growth(df, ward, category, growth_type):
    if growth_type.lower() != "mom":
        raise ValueError("Only MoM growth is supported.")
    data = df[(df["ward"]==ward) & (df["category"]==category)].sort_values("period").copy()
    rows=[]
    prev=None
    for _,r in data.iterrows():
        if pd.isna(r["actual_spend"]) or prev is None or pd.isna(prev):
            growth="NOT COMPUTED"
        else:
            growth=((r["actual_spend"]-prev)/prev)*100
            growth=round(growth,2)
        rows.append({
            "period":r["period"],
            "actual_spend":r["actual_spend"],
            "formula":"((Current-Previous)/Previous)*100",
            "growth":growth
        })
        prev=r["actual_spend"]
    return pd.DataFrame(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--ward",required=True)
    ap.add_argument("--category",required=True)
    ap.add_argument("--growth-type",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    df=load_dataset(args.input)
    out=compute_growth(df,args.ward,args.category,args.growth_type)
    out.to_csv(args.output,index=False)
    print(f"Saved {args.output}")

if __name__=="__main__":
    main()
