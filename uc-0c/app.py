import argparse
import pandas as pd

# ---------- Helper: Normalize text ----------
def normalize(text):
    return str(text).replace("–", "-").strip().lower()


# ---------- Load Dataset ----------
def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"Error loading file: {e}")

    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    for col in required_columns:
        if col not in df.columns:
            raise Exception(f"Missing required column: {col}")

    # Show null rows
    null_rows = df[df["actual_spend"].isnull()]
    if not null_rows.empty:
        print("⚠️ Null values found:")
        print(null_rows[["period", "ward", "category", "notes"]])

    return df


# ---------- Compute Growth ----------
def compute_growth(df, ward, category, growth_type):
    if not growth_type:
        raise Exception("Growth type not specified. Refusing to guess.")

    if growth_type.lower() != "mom":
        raise Exception("Only MoM growth supported. Refusing invalid type.")

    # Normalize dataset for safe matching
    df["ward_norm"] = df["ward"].apply(normalize)
    df["category_norm"] = df["category"].apply(normalize)

    ward_norm = normalize(ward)
    category_norm = normalize(category)

    # Filter safely
    filtered = df[
        (df["ward_norm"] == ward_norm) &
        (df["category_norm"] == category_norm)
    ].copy()

    if filtered.empty:
        print("Available wards:", df["ward"].unique())
        print("Available categories:", df["category"].unique())
        raise Exception("No data found for given ward and category.")

    filtered = filtered.sort_values("period")

    results = []
    prev_value = None

    for _, row in filtered.iterrows():
        period = row["period"]
        actual = row["actual_spend"]
        note = row["notes"]

        # Handle NULL
        if pd.isnull(actual):
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "Not computed",
                "formula": f"NULL value — {note}"
            })
            prev_value = None
            continue

        # First value
        if prev_value is None:
            growth = "N/A"
            formula = "First value — no previous data"
        else:
            growth_value = ((actual - prev_value) / prev_value) * 100
            growth = f"{round(growth_value, 2)}%"
            formula = f"(({actual} - {prev_value}) / {prev_value}) * 100"

        results.append({
            "period": period,
            "actual_spend": actual,
            "growth": growth,
            "formula": formula
        })

        prev_value = actual

    return pd.DataFrame(results)


# ---------- Main ----------
def main():
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
    print(f"✅ Output saved to {args.output}")


if __name__ == "__main__":
    main()