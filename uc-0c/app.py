"""UC-0C budget growth calculator CLI."""
import argparse
import sys

import pandas as pd

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(path):
    df = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        print(f"ERROR: Missing required columns: {', '.join(missing)}")
        sys.exit(1)

    null_rows = df[df["actual_spend"].isna()]
    print(f"Null actual_spend rows: {len(null_rows)}")
    for _, row in null_rows.iterrows():
        reason = "" if pd.isna(row.get("notes")) else str(row.get("notes"))
        print(
            f"- {row['period']} | {row['ward']} | {row['category']} | Reason: {reason}"
        )

    return df


def format_number(value):
    return f"{value:.1f}"


def compute_growth(df, ward, category, growth_type):
    filtered = df[(df["ward"] == ward) & (df["category"] == category)].copy()
    if filtered.empty:
        print("ERROR: No rows found for the specified ward and category.")
        sys.exit(1)

    filtered["period_dt"] = pd.to_datetime(filtered["period"], format="%Y-%m")
    filtered = filtered.sort_values("period_dt")

    if growth_type == "MoM":
        prev_series = filtered["actual_spend"].shift(1)
    else:
        period_map = filtered.set_index("period_dt")["actual_spend"].to_dict()
        prev_series = filtered["period_dt"].apply(
            lambda d: period_map.get(d - pd.DateOffset(years=1))
        )

    output_rows = []
    for (_, row), prev_value in zip(filtered.iterrows(), prev_series):
        actual_value = row["actual_spend"]
        null_flag = ""
        null_reason = ""
        formula = ""
        growth_pct = ""
        prev_spend = ""

        if pd.isna(actual_value):
            null_flag = "NULL_FLAGGED"
            null_reason = "" if pd.isna(row.get("notes")) else str(row.get("notes"))
            growth_pct = "NOT COMPUTED"
        elif pd.isna(prev_value):
            growth_pct = "SKIPPED (prev period null)"
        else:
            actual_num = float(actual_value)
            prev_num = float(prev_value)
            prev_spend = round(prev_num, 1)
            formula = f"({format_number(actual_num)}-{format_number(prev_num)})/{format_number(prev_num)}*100"
            growth_pct = round(((actual_num - prev_num) / prev_num) * 100, 1)

        output_rows.append(
            {
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "actual_spend": "" if pd.isna(actual_value) else round(float(actual_value), 1),
                "prev_spend": prev_spend,
                "formula": formula,
                "growth_pct": growth_pct,
                "null_flag": null_flag,
                "null_reason": null_reason,
            }
        )

    output_df = pd.DataFrame(
        output_rows,
        columns=[
            "period",
            "ward",
            "category",
            "actual_spend",
            "prev_spend",
            "formula",
            "growth_pct",
            "null_flag",
            "null_reason",
        ],
    )

    return output_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=False)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = load_dataset(args.input)

    if not args.growth_type or args.growth_type not in {"MoM", "YoY"}:
        print("ERROR: --growth-type is required. Specify MoM or YoY.")
        sys.exit(1)

    if "all" in args.ward.lower() or "all" in args.category.lower():
        print("ERROR: Aggregation across wards or categories is not permitted.")
        sys.exit(1)

    output_df = compute_growth(df, args.ward, args.category, args.growth_type)
    output_df.to_csv(args.output, index=False)

    null_flagged = (output_df["null_flag"] == "NULL_FLAGGED").sum()
    computed = sum(isinstance(val, float) for val in output_df["growth_pct"])
    print(f"Computed rows: {computed}")
    print(f"Null-flagged rows: {null_flagged}")


if __name__ == "__main__":
    main()
