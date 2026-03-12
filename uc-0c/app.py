import argparse
import csv

def load_dataset(file_path):
    data = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert actual_spend to float if present, else keep None
            row["actual_spend"] = float(row["actual_spend"]) if row["actual_spend"] not in ("", "NULL") else None
            data.append(row)
    return data

def compute_growth(dataset, ward, category, growth_type):
    result = []
    # Filter by ward and category
    filtered = [r for r in dataset if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError("No data for specified ward/category")

    prev_value = None
    for row in filtered:
        actual = row["actual_spend"]
        formula = growth_type + "_formula"
        growth = None
        flagged = False
        if actual is None:
            flagged = True
        elif prev_value is not None and prev_value != 0:
            if growth_type == "MoM":
                growth = (actual - prev_value)/prev_value*100
            elif growth_type == "YoY":
                growth = None  # placeholder for YoY if multiple years
        result.append({
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": actual if actual is not None else "NULL",
            "formula": formula,
            "growth": f"{growth:.1f}%" if growth is not None else None,
            "flag": "NULL_ROW" if flagged else ""
        })
        prev_value = actual if actual is not None else prev_value
    return result

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Computation")
    parser.add_argument("--input", required=True, help="Path to ward_budget CSV file")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "formula", "growth", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()