import argparse
import pandas as pd

def load_dataset(file_path):
    df = pd.read_csv(file_path)

    null_rows = df[df["actual_spend"].isnull()]

    print("Null rows detected:")
    for _, row in null_rows.iterrows():
        print(f"{row['period']} | {row['ward']} | {row['category']} → {row['notes']}")

    return df


def compute_growth(df, ward, category, growth_type):

    if not growth_type:
        raise Exception("Growth type required")

    data = df[(df["ward"] == ward) & (df["category"] == category)]
    data = data.sort_values("period")

    results = []

    for i in range(len(data)):
        row = data.iloc[i]
        current = row["actual_spend"]

        if pd.isnull(current):
            results.append({
                "period": row["period"],
                "growth": "NULL",
                "formula": "Skipped due to NULL",
                "flag": row["notes"]
            })
            continue

        if i == 0:
            results.append({
                "period": row["period"],
                "growth": "N/A",
                "formula": "No previous month",
                "flag": ""
            })
            continue

        prev = data.iloc[i-1]["actual_spend"]

        if pd.isnull(prev):
            results.append({
                "period": row["period"],
                "growth": "NULL",
                "formula": "Previous month NULL",
                "flag": "Previous value missing"
            })
            continue

        growth = ((current - prev) / prev) * 100

        results.append({
            "period": row["period"],
            "growth": round(growth, 2),
            "formula": f"({current}-{prev})/{prev}*100",
            "flag": ""
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    df = load_dataset(args.input)
    result = compute_growth(df, args.ward, args.category, args.growth_type)

    result.to_csv(args.output, index=False)

    print("Done!")