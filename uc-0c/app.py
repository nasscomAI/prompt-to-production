import argparse
import pandas as pd


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(input_path):
    """Load and validate the ward budget CSV."""
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_path}")
    except Exception as e:
        raise ValueError(f"Could not read input file: {e}")

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Treat blank actual_spend values as null
    df["actual_spend"] = pd.to_numeric(
        df["actual_spend"], errors="coerce"
    )

    null_rows = df[df["actual_spend"].isna()]

    print(f"Null actual_spend count: {len(null_rows)}")

    if not null_rows.empty:
        print("\nNull rows:")
        for _, row in null_rows.iterrows():
            print(
                f"{row['period']} | {row['ward']} | "
                f"{row['category']} | Reason: {row['notes']}"
            )

    return df


def compute_growth(df, ward, category, growth_type):
    """Calculate growth for the requested ward and category."""

    if not growth_type:
        raise ValueError(
            "Growth type is required. Specify --growth-type, "
            "for example MoM."
        )

    if growth_type.upper() != "MOM":
        raise ValueError(
            "Unsupported growth type. UC-0C requires an explicitly "
            "specified growth type; this implementation supports MoM."
        )

    ward_data = df[df["ward"] == ward].copy()
    ward_data = ward_data[ward_data["category"] == category].copy()

    if ward_data.empty:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    ward_data["period"] = pd.to_datetime(
        ward_data["period"], format="%Y-%m"
    )

    ward_data = ward_data.sort_values("period")

    results = []

    previous_spend = None
    previous_period = None

    for _, row in ward_data.iterrows():

        current_spend = row["actual_spend"]

        # Current value is null
        if pd.isna(current_spend):
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"].strftime("%Y-%m"),
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": "Not computed because actual_spend is NULL",
                "null_reason": row["notes"],
            })

            previous_spend = None
            previous_period = row["period"]
            continue

        # No previous valid value
        if previous_spend is None:
            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"].strftime("%Y-%m"),
                "actual_spend": current_spend,
                "growth": "N/A",
                "formula": "Not computed: no previous valid month",
                "null_reason": "",
            })
        else:
            growth = (
                (current_spend - previous_spend)
                / previous_spend
            ) * 100

            formula = (
                f"(({current_spend:.2f} - {previous_spend:.2f}) "
                f"/ {previous_spend:.2f}) * 100"
            )

            results.append({
                "ward": ward,
                "category": category,
                "period": row["period"].strftime("%Y-%m"),
                "actual_spend": current_spend,
                "growth": f"{growth:+.1f}%",
                "formula": formula,
                "null_reason": "",
            })

        previous_spend = current_spend
        previous_period = row["period"]

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ward/category budget growth."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file"
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Ward name"
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Category name"
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth type, e.g. MoM"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path"
    )

    args = parser.parse_args()

    try:
        df = load_dataset(args.input)

        result = compute_growth(
            df,
            args.ward,
            args.category,
            args.growth_type
        )

        result.to_csv(args.output, index=False)

        print(f"\nOutput successfully written to: {args.output}")

    except ValueError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()