import argparse
import pandas as pd
def compute_growth(input_file, ward, category, output_file):

    df = pd.read_csv(input_file)

    filtered = df[(df["ward"] == ward) & (df["category"] == category)]

    filtered = filtered.sort_values("period")

    results = []

    prev = None

    for _, row in filtered.iterrows():

        if pd.isna(row["actual_spend"]):
            results.append({
                "period": row["period"],
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": "null value"
            })
            prev=None
            continue

        if prev is None:
            growth="N/A"
            formula="first value"
        else:
            growth = ((row["actual_spend"]-prev)/prev)*100
            formula=f"({row['actual_spend']}-{prev})/{prev}"

        results.append({
            "period":row["period"],
            "actual_spend":row["actual_spend"],
            "growth":growth,
            "formula":formula
        })

        prev=row["actual_spend"]

    pd.DataFrame(results).to_csv(output_file,index=False)

    print("Growth calculation done")


def main():

    parser=argparse.ArgumentParser()

    parser.add_argument("--input",required=True)
    parser.add_argument("--ward",required=True)
    parser.add_argument("--category",required=True)
    parser.add_argument("--growth-type",required=True)
    parser.add_argument("--output",required=True)

    args=parser.parse_args()

    compute_growth(args.input,args.ward,args.category,args.output)


if __name__=="__main__":
    main()