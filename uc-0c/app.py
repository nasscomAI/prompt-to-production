import argparse
import csv
import sys


def load_dataset(input_path):
    data = []
    nulls = []
    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            val = row.get("actual_spend", "").strip()
            if val.lower() == "null" or val == "":
                nulls.append(
                    {"row_idx": i + 1, "ward": row["ward"], "category": row["category"], "reason": row.get("notes", "Unknown")}
                )
            data.append(row)
    
    if nulls:
        print(f"Validation Notice: Found {len(nulls)} null values in the dataset.")
        for n in nulls:
            print(f"- Row {n['row_idx']} ({n['ward']} - {n['category']}): {n['reason']}")
    return data


def compute_growth(dataset, ward, category, growth_type):
    if not growth_type:
        return "REFUSAL: --growth-type not specified. Cannot assume formula."
        
    if ward.lower() == "any" or category.lower() == "any" or not ward or not category:
        return "REFUSAL: Aggregation across multiple wards or categories is not permitted based on system directives."

    subset = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    subset.sort(key=lambda x: x["period"])

    output = []
    
    for i in range(len(subset)):
        current_row = subset[i]
        period = current_row["period"]
        spend_str = current_row.get("actual_spend", "").strip()
        
        # Null handling
        if spend_str.lower() == "null" or spend_str == "":
            flag_msg = f"NULL ({current_row.get('notes', 'No data')})"
            output.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": flag_msg,
                "growth": "Must be flagged — not computed",
                "formula_used": "N/A - Cannot compute with missing data"
            })
            continue

        spend_val = float(spend_str)
        
        if growth_type.lower() == "mom":
            if i == 0:
                output.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": spend_val,
                    "growth": "N/A",
                    "formula_used": "Base period"
                })
            else:
                prev_spend_str = subset[i-1].get("actual_spend", "").strip()
                if prev_spend_str.lower() == "null" or prev_spend_str == "":
                    output.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": spend_val,
                        "growth": "N/A",
                        "formula_used": "Previous period data is NULL"
                    })
                else:
                    prev_val = float(prev_spend_str)
                    if prev_val == 0:
                        growth_val = 0.0
                    else:
                        growth_val = ((spend_val - prev_val) / prev_val) * 100
                    
                    formula = f"(({spend_val} - {prev_val}) / {prev_val}) * 100"
                    
                    sign = "+" if growth_val > 0 else ""
                    # Optional notes attachment from data to mimic demo "monsoon spike"
                    note_suffix = ""
                    if "spike" in current_row.get("notes", "").lower() or "monsoon" in current_row.get("notes", "").lower():
                        note_suffix = f" ({current_row.get('notes', '')})"
                    elif "post" in current_row.get("notes", "").lower():
                        note_suffix = f" ({current_row.get('notes', '')})"
                    
                    output.append({
                        "period": period,
                        "ward": ward,
                        "category": category,
                        "actual_spend": spend_val,
                        "growth": f"{sign}{growth_val:.1f}%{note_suffix}".strip(),
                        "formula_used": formula
                    })
    
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--growth-type", default="")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = load_dataset(args.input)
    result = compute_growth(data, args.ward, args.category, args.growth_type)
    
    if isinstance(result, str) and result.startswith("REFUSAL"):
        print(f"Error: {result}")
        sys.exit(1)
        
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula_used"])
        writer.writeheader()
        writer.writerows(result)
        
    print(f"Success! Output written to {args.output}")

if __name__ == "__main__":
    main()
