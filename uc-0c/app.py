import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = pd.read_csv(args.input)

    df = df[
        (df["ward"] == args.ward) &
        (df["category"] == args.category)
    ].copy()

    df["actual_spend"] = pd.to_numeric(df["actual_spend"], errors="coerce")

    df["Formula"] = "(Current-Previous)/Previous*100"

    df["Growth"] = df["actual_spend"].pct_change() * 100

    df.loc[df["actual_spend"].isna(), "Growth"] = "NULL"

    df.to_csv(args.output, index=False)

    print("Growth output saved to", args.output)

if __name__ == "__main__":
    main()