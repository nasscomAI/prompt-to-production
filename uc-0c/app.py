"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from collections import defaultdict


# -----------------------------
# Skill 1: load_dataset
# -----------------------------
def load_dataset(file_path):
    data = []
    null_rows = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            required_cols = {
                "period", "ward", "category",
                "budgeted_amount", "actual_spend", "notes"
            }

            if not required_cols.issubset(reader.fieldnames):
                raise ValueError("Missing required columns in CSV")

            for row in reader:
                # Handle null actual_spend
                if row["actual_spend"] == "" or row["actual_spend"] is None:
                    row["actual_spend"] = None
                    null_rows.append(row)
                else:
                    row["actual_spend"] = float(row["actual_spend"])

                data.append(row)

    except Exception as e:
        raise ValueError(f"Error loading dataset: {e}")

    return data, null_rows


# -----------------------------
# Skill 2: compute_growth
# -----------------------------
def compute_growth(data, ward, category, growth_type):
    if not growth_type:
        raise ValueError("growth_type is required (MoM or YoY)")

    if growth_type not in ["MoM"]:
        raise ValueError("Only MoM supported in this implementation")

    # Filter data
    filtered = [
        row for row in data
        if row["ward"] == ward and row["category"] == category
    ]

    if not filtered:
        raise ValueError("No data found for given ward/category")

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []

    prev_value = None

    for row in filtered:
        period = row["period"]
        value = row["actual_spend"]

        if value is None:
            results.append({
                "period": period,
                "actual_spend": "NULL",
                "growth": "NULL",
                "formula": f"NULL (reason: {row['notes']})"
            })
            prev_value = None
            continue

        if prev_value is None:
            results.append({
                "period": period,
                "actual_spend": value,
                "growth": "N/A",
                "formula": "No previous month to compare"
            })
        else:
            growth = ((value - prev_value) / prev_value) * 100
            formula = f"(({value} - {prev_value}) / {prev_value}) * 100"

            results.append({
                "period": period,
                "actual_spend": value,
                "growth": f"{round(growth, 2)}%",
                "formula": formula
            })

        prev_value = value

    return results


# -----------------------------
# Main
# -----------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        data, null_rows = load_dataset(args.input)

        # Enforcement: refuse aggregation
        if args.ward.lower() == "all" or args.category.lower() == "all":
            raise ValueError("Aggregation across wards/categories is not allowed")

        results = compute_growth(
            data,
            args.ward,
            args.category,
            args.growth_type
        )

        # Write output CSV
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["period", "actual_spend", "growth", "formula"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(results)

        print("✅ Growth output generated successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()