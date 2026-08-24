"""
UC-0C Number That Looks Right
"""
import argparse
import csv

def load_dataset(file_path: str) -> tuple:
    rows = []
    nulls = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row['actual_spend'].strip():
                nulls.append(row)
            rows.append(row)
    print(f"Loaded {len(rows)} rows. Found {len(nulls)} deliberate nulls explicitly flagged for transparency.")
    return rows, nulls

def compute_growth(rows: list, target_ward: str, target_category: str, growth_type: str) -> list:
    if not growth_type:
        raise ValueError("REFUSAL: --growth-type must be provided explicitly. Will not guess MoM or YoY.")
    if not target_ward or not target_category or target_ward.lower() == "all" or target_category.lower() == "all":
        raise ValueError("REFUSAL: Never aggregate across wards or categories.")
        
    filtered = [r for r in rows if r['ward'] == target_ward and r['category'] == target_category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prior_spend = None
    
    for row in filtered:
        period = row['period']
        current_spend_str = row['actual_spend'].strip()
        
        if not current_spend_str:
            results.append({
                "period": period,
                "ward": target_ward,
                "category": target_category,
                "actual_spend": "NULL",
                "mom_growth": "NULL - " + row.get("notes", "No reason provided"),
                "formula": "NULL handling engaged"
            })
            prior_spend = None  # Reset prior spend since logic chain broken
            continue
            
        current_spend = float(current_spend_str)
        
        if prior_spend is None:
            growth_str = "n/a"
            formula = "n/a (first valid period)"
        else:
            growth = ((current_spend - prior_spend) / prior_spend) * 100
            sign = "+" if growth > 0 else ""
            growth_str = f"{sign}{growth:.1f}%"
            formula = f"({current_spend} - {prior_spend}) / {prior_spend} * 100"
            
        results.append({
            "period": period,
            "ward": target_ward,
            "category": target_category,
            "actual_spend": current_spend,
            "mom_growth": growth_str,
            "formula": formula
        })
        prior_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    try:
        rows, nulls = load_dataset(args.input)
        output_data = compute_growth(rows, args.ward, args.category, args.growth_type)
        
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            if output_data:
                writer = csv.DictWriter(f, fieldnames=output_data[0].keys())
                writer.writeheader()
                writer.writerows(output_data)
        print(f"Done. Wrote {len(output_data)} rows to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
