import csv
import os

def process_budget_data(input_file):
    """
    Process budget data with strict 'God-level' magistrate logic:
    - Grounding on 'notes' column.
    - Explicit refusal for nulls.
    - Precision rounding.
    """
    category_data = {}
    audit_log = []

    if not os.path.exists(input_file):
        return None, [f"ERROR: Input file {input_file} not found."]

    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 2): # Start from line 2
            category = row['category']
            actual_spend_str = row['actual_spend'].strip()
            notes = row['notes'].strip()
            ward = row['ward']
            period = row['period']

            if category not in category_data:
                category_data[category] = {"sum": 0.0, "count": 0, "excluded": []}

            if not actual_spend_str:
                # Magistrate Refusal Logic
                reason = notes if notes else "No data and no explanation provided"
                category_data[category]["excluded"].append({
                    "row": i,
                    "ward": ward,
                    "period": period,
                    "reason": reason
                })
                audit_log.append(f"[REFUSAL] Row {i}: {category} in {ward} ({period}) excluded. Reason: {reason}")
            else:
                try:
                    spend = float(actual_spend_str)
                    category_data[category]["sum"] += spend
                    category_data[category]["count"] += 1
                except ValueError:
                    audit_log.append(f"[ERROR] Row {i}: Invalid number '{actual_spend_str}'. Excluded.")

    results = []
    for category, stats in category_data.items():
        valid_count = stats["count"]
        excluded_count = len(stats["excluded"])
        total_count = valid_count + excluded_count
        
        # Rule 11: 50% Threshold Enforcement
        if total_count > 0 and (valid_count / total_count) < 0.5:
            avg_val = "STRICT_REFUSAL: Data Integrity Threshold Not Met (<50%)"
        elif valid_count > 0:
            avg_val = round(stats["sum"] / valid_count, 2)
        else:
            avg_val = "STRICT_REFUSAL: No valid numerical data"

        coverage = round((valid_count / total_count) * 100, 1) if total_count > 0 else 0.0
        
        results.append({
            "Category": category,
            "Average_Actual_Spend": avg_val,
            "Valid_Samples": valid_count,
            "Excluded_Samples": excluded_count,
            "Coverage_Percent": coverage
        })

    return results, audit_log

def main():
    input_path = os.path.join("data", "budget", "ward_budget.csv")
    output_path = os.path.join("uc-0c", "growth_output.csv")
    log_path = os.path.join("uc-0c", "audit_log.txt")

    print(f"Starting District Budget Audit: {input_path}")
    results, audit_log = process_budget_data(input_path)

    if results is None:
        print(audit_log[0])
        return

    # Write Results
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        fieldnames = ["Category", "Average_Actual_Spend", "Valid_Samples", "Excluded_Samples", "Coverage_Percent"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Write Audit Log
    with open(log_path, mode='w', encoding='utf-8') as f:
        f.write("--- DISTRICT AUDIT MAGISTRATE LOG ---\n")
        f.write("\n".join(audit_log))

    print(f"Audit Complete.")
    print(f"- Statistical data written to {output_path}")
    print(f"- Detailed audit log written to {log_path}")

if __name__ == "__main__":
    main()
