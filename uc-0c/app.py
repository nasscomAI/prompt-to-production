import argparse
import csv
import sys
from typing import Dict, List, Tuple


def load_dataset(file_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Reads CSV file, validates columns, and flags null actual_spend rows."""
    records = []
    null_flags = []
    required_columns = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not required_columns.issubset(set(reader.fieldnames or [])):
                missing = required_columns - set(reader.fieldnames or [])
                raise ValueError(f"CSV schema missing required columns: {missing}")

            for idx, row in enumerate(reader, start=2):
                val = row["actual_spend"].strip() if row["actual_spend"] else ""
                if val == "":
                    null_flags.append({
                        "line": str(idx),
                        "period": row["period"],
                        "ward": row["ward"],
                        "category": row["category"],
                        "notes": row["notes"]
                    })
                records.append(row)
    except FileNotFoundError:
        print(f"Error: File not found at path '{file_path}'", file=sys.stderr)
        sys.exit(1)

    print(f"[load_dataset] Successfully loaded {len(records)} rows.")
    print(f"[load_dataset] Flagged {len(null_flags)} null actual_spend rows:")
    for flag in null_flags:
        print(f"  - Line {flag['line']}: {flag['period']} | {flag['ward']} | {flag['category']} -> Reason: {flag['notes']}")
    
    return records, null_flags


def compute_growth(
    records: List[Dict[str, str]], ward: str, category: str, growth_type: str
) -> List[Dict[str, str]]:
    """Computes growth (MoM/YoY) per period for a specific ward and category."""
    # Enforcement Rule 4: Check growth-type
    if not growth_type or growth_type.strip() == "":
        raise ValueError("Refusal: --growth-type was not specified. Options: MoM, YoY. Refusing to guess.")

    # Enforcement Rule 1: Refuse aggregation across all wards or categories
    if not ward or ward.lower() in ["all", "any", "total"]:
        raise ValueError("Refusal: Cannot aggregate across all wards. Specify a single ward.")
    if not category or category.lower() in ["all", "any", "total"]:
        raise ValueError("Refusal: Cannot aggregate across all categories. Specify a single category.")

    # Filter records strictly for target ward and category
    filtered = [
        r for r in records
        if r["ward"].strip() == ward.strip() and r["category"].strip() == category.strip()
    ]
    
    if not filtered:
        raise ValueError(f"No records found matching ward='{ward}' and category='{category}'.")

    # Sort strictly by period
    filtered.sort(key=lambda x: x["period"])

    results = []
    formula_desc = "(Actual_t - Actual_{t-1}) / Actual_{t-1} * 100" if growth_type.upper() == "MoM" else "(Actual_t - Actual_{t-12}) / Actual_{t-12} * 100"

    for i, row in enumerate(filtered):
        period = row["period"]
        curr_val_str = row["actual_spend"].strip() if row["actual_spend"] else ""
        notes = row["notes"].strip()

        row_result = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": curr_val_str if curr_val_str != "" else "NULL",
            "growth_type": growth_type,
            "growth_output": "",
            "formula_used": formula_desc,
            "status": "VALID"
        }

        # Handle null current row (Enforcement Rule 2)
        if curr_val_str == "":
            row_result["growth_output"] = "NULL"
            row_result["status"] = f"FLAGGED: {notes}"
            results.append(row_result)
            continue

        curr_val = float(curr_val_str)

        # Determine prior row index based on MoM vs YoY
        offset = 1 if growth_type.upper() == "MoM" else 12
        prev_idx = i - offset

        if prev_idx < 0:
            row_result["growth_output"] = "N/A (Base Period)"
        else:
            prev_row = filtered[prev_idx]
            prev_val_str = prev_row["actual_spend"].strip() if prev_row["actual_spend"] else ""

            if prev_val_str == "":
                row_result["growth_output"] = "NULL"
                row_result["status"] = f"FLAGGED: Prior period actual_spend was NULL ({prev_row['notes']})"
            else:
                prev_val = float(prev_val_str)
                if prev_val == 0:
                    row_result["growth_output"] = "N/A (Div by zero)"
                else:
                    growth_pct = ((curr_val - prev_val) / prev_val) * 100
                    prefix = "+" if growth_pct > 0 else ""
                    row_result["growth_output"] = f"{prefix}{growth_pct:.1f}%"

        results.append(row_result)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Infrastructure Spend Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input budget CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward name")
    parser.add_argument("--category", required=True, help="Specific budget category name")
    parser.add_argument("--growth-type", required=False, default="", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output growth CSV file")

    args = parser.parse_args()

    # Step 1: Load and check dataset
    records, null_flags = load_dataset(args.input)

    # Step 2: Calculate growth strictly obeying enforcement rules
    try:
        results = compute_growth(records, args.ward, args.category, args.growth_type)
    except ValueError as err:
        print(f"\n[ENFORCEMENT REFUSAL / ERROR]: {err}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Write per-ward per-category output table
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth_output", "formula_used", "status"]
    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[Success] Per-ward growth table saved to '{args.output}'.")


if __name__ == "__main__":
    main()