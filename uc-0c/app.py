"""
UC-0C app.py — Growth calculator for ward budget data.
Implements load_dataset and compute_growth per skills.md, enforcing
the refusal/flagging rules defined in agents.md.
"""
import argparse
import sys
import pandas as pd

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(path):
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {missing}")

    null_rows = df[df["actual_spend"].isna()]
    if not null_rows.empty:
        print(f"[load_dataset] {len(null_rows)} row(s) have null actual_spend:")
        for _, row in null_rows.iterrows():
            reason = row["notes"] if pd.notna(row["notes"]) else "no reason given"
            print(f"  - {row['period']} | {row['ward']} | {row['category']} | reason: {reason}")
    return df


def compute_growth(df, ward, category, growth_type):
    if not ward or not category:
        raise ValueError(
            "REFUSED: aggregation across wards/categories is not permitted. "
            "Both --ward and --category must be specified explicitly."
        )
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            "REFUSED: --growth-type must be explicitly 'MoM' or 'YoY'. Refusing to guess."
        )

    subset = df[(df["ward"] == ward) & (df["category"] == category)] \
        .sort_values("period").reset_index(drop=True)
    if subset.empty:
        raise ValueError(f"REFUSED: no rows found for ward='{ward}', category='{category}'.")

    lag = 1 if growth_type == "MoM" else 12
    results = []
    for i, row in subset.iterrows():
        period, actual = row["period"], row["actual_spend"]

        if pd.isna(actual):
            results.append({"period": period, "ward": ward, "category": category,
                             "actual_spend": None, "growth_pct": None,
                             "formula": "N/A - value flagged as null",
                             "flag": f"NULL - {row['notes']}"})
            continue

        if i < lag:
            results.append({"period": period, "ward": ward, "category": category,
                             "actual_spend": actual, "growth_pct": None,
                             "formula": "N/A - insufficient prior period(s)",
                             "flag": ""})
            continue

        prev_actual = subset.loc[i - lag, "actual_spend"]
        if pd.isna(prev_actual):
            results.append({"period": period, "ward": ward, "category": category,
                             "actual_spend": actual, "growth_pct": None,
                             "formula": "N/A - prior period value is null",
                             "flag": "PRIOR PERIOD NULL"})
            continue

        growth = (actual - prev_actual) / prev_actual * 100
        results.append({"period": period, "ward": ward, "category": category,
                         "actual_spend": actual, "growth_pct": round(growth, 1),
                         "formula": f"({actual} - {prev_actual}) / {prev_actual} * 100",
                         "flag": ""})

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", dest="growth_type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = load_dataset(args.input)

    try:
        result_df = compute_growth(df, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    result_df.to_csv(args.output, index=False)
    print(f"Wrote {len(result_df)} rows to {args.output}")


if __name__ == "__main__":
    main()