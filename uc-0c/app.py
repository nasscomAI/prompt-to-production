"""
UC-0C app.py — Budget-growth computation agent.
Processes per-ward per-category growth from ward_budget.csv.
See README.md for run command and expected behaviour.
"""
import argparse
import sys

import pandas as pd


REQUIRED_COLS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Cannot parse CSV: {e}")

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    null_mask = df["actual_spend"].isna()
    null_count = null_mask.sum()
    print(f"Null actual_spend count: {null_count}")
    if null_count > 0:
        print("Rows with null actual_spend:")
        for _, r in df[null_mask].iterrows():
            note = r["notes"] if pd.notna(r["notes"]) else "(no note)"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | notes: {note}")

    return df


def compute_growth(df, ward, category, growth_type):
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"growth_type must be 'MoM' or 'YoY', got '{growth_type}'")

    subset = df[(df["ward"] == ward) & (df["category"] == category)]
    if subset.empty:
        valid_wards = sorted(df["ward"].unique())
        valid_cats = sorted(df["category"].unique())
        raise ValueError(
            f"Ward '{ward}' or category '{category}' not found in data.\n"
            f"Valid wards: {valid_wards}\nValid categories: {valid_cats}"
        )

    subset = subset.sort_values("period").reset_index(drop=True)

    null_mask = subset["actual_spend"].isna()
    if null_mask.any():
        print(f"Warning: {null_mask.sum()} null actual_spend row(s) in selected data. Flagging with notes.")

    shift_n = 1 if growth_type == "MoM" else 12
    subset["previous_spend"] = subset["actual_spend"].shift(shift_n)

    rows = []
    for _, row in subset.iterrows():
        entry = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": row["actual_spend"],
            "previous_spend": row["previous_spend"],
            "growth_type": growth_type,
        }

        if pd.isna(row["actual_spend"]):
            entry["growth_value"] = None
            entry["null_reason"] = row["notes"] if pd.notna(row["notes"]) else "No reason given"
            entry["formula"] = "NULL — not computed"
        elif pd.isna(row["previous_spend"]):
            entry["growth_value"] = None
            entry["null_reason"] = None
            entry["formula"] = "No prior period available"
        else:
            curr = row["actual_spend"]
            prev = row["previous_spend"]
            growth_val = ((curr - prev) / prev) * 100
            entry["growth_value"] = round(growth_val, 2)
            entry["null_reason"] = None
            entry["formula"] = f"(({curr} - {prev}) / {prev}) * 100"

        rows.append(entry)

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Budget-growth computation agent")
    parser.add_argument("--input", required=True, help="Path to ward_budget CSV")
    parser.add_argument("--ward", required=True, help="Ward name to compute growth for")
    parser.add_argument("--category", required=True, help="Category name to compute growth for")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type must be specified ('MoM' or 'YoY'). Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    df = load_dataset(args.input)
    result = compute_growth(df, args.ward, args.category, args.growth_type)
    result.to_csv(args.output, index=False)
    print(f"Output written to {args.output} ({len(result)} rows)")


if __name__ == "__main__":
    main()
