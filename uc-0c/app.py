"""
UC-0C app.py — Number That Looks Right.
Implements the rules from agents.md systematically.
"""
import argparse
import csv
import sys
import os

def load_dataset(file_path):
    dataset = []
    null_report = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get("actual_spend", "").strip()
            if not val or val.lower() == "null":
                null_report.append(f"{row.get('period', '')} | {row.get('ward', '')} | {row.get('category', '')} | NULL Reason: {row.get('notes', '')}")
            dataset.append(row)
    return dataset, null_report

def compute_growth(dataset, ward, category, growth_type):
    # Enforce constraints
    if not growth_type:
        raise ValueError("Refusal: --growth-type not specified, will not guess.")
    if not ward or not category:
        raise ValueError("Refusal: Never aggregate across wards or categories unless explicitly instructed.")

    # Filter dataset
    filtered = [row for row in dataset if row["ward"] == ward and row["category"] == category]
    
    # Sort by period
    filtered.sort(key=lambda x: x["period"])
    
    output_lines = [f"Growth Table for {ward} - {category} (Type: {growth_type})"]
    output_lines.append(f"Period | Actual Spend | {growth_type} Growth | Notes | Formula")
    output_lines.append("-" * 80)
    
    prev_val = None
    for row in filtered:
        period = row["period"]
        val = row.get("actual_spend", "").strip()
        notes = row.get("notes", "")

        if not val or val.lower() == "null":
            output_lines.append(f"{period} | NULL | Flagged — not computed | {notes} | n/a")
            prev_val = None # Reset prev
            continue
            
        actual_spend = float(val)
        if prev_val is None:
            output_lines.append(f"{period} | {actual_spend} | n/a | {notes} | No previous data")
        else:
            diff = actual_spend - prev_val
            pct = (diff / prev_val) * 100
            sign = "+" if pct > 0 else ""
            formula = f"(({actual_spend} - {prev_val}) / {prev_val}) * 100"
            output_lines.append(f"{period} | {actual_spend} | {sign}{pct:.1f}% | {notes} | {formula}")
        
        prev_val = actual_spend
        
    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False, dest="growth_type")
    
    args = parser.parse_args()
    
    report = []
    
    try:
        dataset, null_report = load_dataset(args.input)
    except FileNotFoundError as e:
        report.append(f"ERROR: {str(e)}")
        dataset = None
        
    if dataset is not None:
        if null_report:
            report.append("NULL VALUES FLAG REPORT:")
            report.extend(null_report)
            report.append("-" * 80)
            
        try:
            results = compute_growth(dataset, args.ward, args.category, args.growth_type)
            report.append(results)
        except ValueError as e:
            report.append(f"ERROR: Agent Refused. {str(e)}")
        
    final_output = "\n".join(report)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print(f"Report successfully written to {args.output}")

if __name__ == "__main__":
    main()
