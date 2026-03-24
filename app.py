import argparse
import csv
import sys

# -------------------------------
# Skill: load_dataset
# -------------------------------
def load_dataset(file_path):
    required_columns = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    dataset = []
    null_rows = []

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # Validate schema
            for col in required_columns:
                if col not in reader.fieldnames:
                    sys.exit(f"Error: Missing required column {col}")

            for row in reader:
                dataset.append(row)
                if row["actual_spend"] == "" or row["actual_spend"] is None:
                    null_rows.append({
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "reason": row["notes"]
                    })

        return dataset, null_rows
    except FileNotFoundError:
        sys.exit("Error: Input file not found.")
    except Exception as e:
        sys.exit(f"Error loading dataset: {e}")

# -------------------------------
# Skill: compute_growth
# -------------------------------
def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        sys.exit("Error: --growth-type not specified. Refusing to guess.")

    if not ward or not category:
        sys.exit("Error: Ward and category must be specified.")

    # Filter dataset strictly by ward and category
    filtered = [row for row in dataset if row["ward"] == ward and row["category"] == category]

    if not filtered:
        sys.exit("Error: No matching data for given ward and category.")

    # Sort by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    prev_spend = None
    for row in filtered:
        period = row["period"]
        actual_spend = row["actual_spend"]
        notes = row["notes"]

        if actual_spend == "" or actual_spend is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth": "FLAGGED",
                "formula": f"Null reason: {notes}"
            })
            prev_spend = None
            continue

        actual_spend = float(actual_spend)

        if growth_type == "MoM":
            if prev_spend is None:
                growth = "N/A"
                formula = "No previous month to compare"
            else:
                try:
                    growth_value = ((actual_spend - prev_spend) / prev_spend) * 100
                    growth = f"{growth_value:+.1f}%"
                    formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                except ZeroDivisionError:
                    growth = "Undefined"
                    formula = "Previous spend was 0"
            prev_spend = actual_spend
        else:
            sys.exit("Error: Unsupported growth_type. Only MoM supported in this UC.")

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "growth": growth,
            "formula": formula
        })

    return results

# -------------------------------
# Output Writer
# -------------------------------
def write_output(results, output_file):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula"]
    try:
        with open(output_file, mode="w", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
    except Exception as e:
        sys.exit(f"Error writing output file: {e}")

# -------------------------------
# Main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Computation App")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Output CSV file path")

    args = parser.parse_args()

    # Load dataset
    dataset, null_rows = load_dataset(args.input)

    # Report null rows explicitly
    if null_rows:
        print("Flagged null rows:")
        for nr in null_rows:
            print(f"{nr['period']} · {nr['ward']} · {nr['category']} → {nr['reason']}")

    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output
    write_output(results, args.output)
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()