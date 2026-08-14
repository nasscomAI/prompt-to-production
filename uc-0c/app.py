"""
UC-0C app.py — Municipal Financial Data Verification Application
Implementation based on RICE prompt (agents.md) and skill specifications (skills.md).
"""
import argparse
import csv
import os
import sys


def load_dataset(input_path: str):
    """
    Reads CSV, validates required schema headers, and audits null actual_spend rows.
    Returns tuple: (all_records, null_audit_records)
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required_headers = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
    records = []
    null_audits = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        if not required_headers.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV header validation failed. Required headers missing.")

        for i, row in enumerate(reader, start=2):
            raw_spend = row.get("actual_spend", "").strip()
            spend_val = None
            if raw_spend != "" and raw_spend.upper() != "NULL":
                try:
                    spend_val = float(raw_spend)
                except ValueError:
                    spend_val = None

            record = {
                "period": row.get("period", "").strip(),
                "ward": row.get("ward", "").strip(),
                "category": row.get("category", "").strip(),
                "budgeted_amount": row.get("budgeted_amount", "").strip(),
                "actual_spend": spend_val,
                "notes": row.get("notes", "").strip(),
            }
            records.append(record)

            if spend_val is None:
                null_audits.append({
                    "row": i,
                    "period": record["period"],
                    "ward": record["ward"],
                    "category": record["category"],
                    "notes": record["notes"],
                })

    return records, null_audits


def compute_growth(records: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes per-period growth for a specific ward and category.
    Strictly enforces non-aggregation and explicit formula rules.
    """
    # Enforcement Rule 1 & Refusal Condition: Refuse all-ward or all-category aggregations
    if not ward or ward.upper() in ["ALL", "ANY", "COMBINED", "*"]:
        raise ValueError("REFUSAL: All-ward aggregation requested. Computations must remain strictly per-ward and per-category.")

    if not category or category.upper() in ["ALL", "ANY", "COMBINED", "*"]:
        raise ValueError("REFUSAL: All-category aggregation requested. Computations must remain strictly per-ward and per-category.")

    # Enforcement Rule 4: Refuse if --growth-type is omitted or invalid
    if not growth_type or growth_type.upper() not in ["MOM", "YOY"]:
        raise ValueError("REFUSAL: Growth type (--growth-type) not specified or invalid. Must be 'MoM' or 'YoY'. Refusing to assume default formula.")

    growth_type = growth_type.upper()

    # Filter records for target ward and category
    filtered = [
        r for r in records
        if r["ward"].lower() == ward.lower() and r["category"].lower() == category.lower()
    ]

    if not filtered:
        raise ValueError(f"No records found matching ward '{ward}' and category '{category}'.")

    # Sort by period chronologically
    filtered.sort(key=lambda x: x["period"])

    output_rows = []

    for idx, curr in enumerate(filtered):
        period = curr["period"]
        curr_spend = curr["actual_spend"]
        notes = curr["notes"]

        # Null Audit & Reporting Rule: Flag null spend rows before computation
        if curr_spend is None:
            output_rows.append({
                "period": period,
                "ward": curr["ward"],
                "category": curr["category"],
                "actual_spend": "NULL",
                "growth_rate": "NULL (Uncomputable)",
                "formula_used": "N/A",
                "notes": notes or "Data missing or omitted",
            })
            continue

        if growth_type == "MOM":
            formula_str = "MoM = (Actual_Spend_t - Actual_Spend_{t-1}) / Actual_Spend_{t-1} * 100"
            if idx == 0:
                growth_rate_str = "N/A (Base Period)"
                formula_str = "Base Period"
            else:
                prev = filtered[idx - 1]
                prev_spend = prev["actual_spend"]
                if prev_spend is None or prev_spend == 0:
                    growth_rate_str = "N/A (Prior period spend is NULL/Zero)"
                else:
                    change_pct = ((curr_spend - prev_spend) / prev_spend) * 100
                    sign = "+" if change_pct > 0 else ""
                    growth_rate_str = f"{sign}{change_pct:.1f}%"
        elif growth_type == "YOY":
            formula_str = "YoY = (Actual_Spend_t - Actual_Spend_{t-12}) / Actual_Spend_{t-12} * 100"
            if idx < 12:
                growth_rate_str = "N/A (Base Period < 12 months)"
                formula_str = "Base Period (< 12m)"
            else:
                prev = filtered[idx - 12]
                prev_spend = prev["actual_spend"]
                if prev_spend is None or prev_spend == 0:
                    growth_rate_str = "N/A (Prior year spend is NULL/Zero)"
                else:
                    change_pct = ((curr_spend - prev_spend) / prev_spend) * 100
                    sign = "+" if change_pct > 0 else ""
                    growth_rate_str = f"{sign}{change_pct:.1f}%"

        output_rows.append({
            "period": period,
            "ward": curr["ward"],
            "category": curr["category"],
            "actual_spend": f"{curr_spend:.1f}",
            "growth_rate": growth_rate_str,
            "formula_used": formula_str,
            "notes": notes,
        })

    return output_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Municipal Financial Data Verification Agent")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Target ward name")
    parser.add_argument("--category", required=False, default=None, help="Target category name")
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="Growth calculation type (MoM or YoY)")
    parser.add_argument("--output", required=True, help="Path to output growth_output.csv")
    args = parser.parse_args()

    try:
        records, null_audits = load_dataset(args.input)
        print(f"Loaded {len(records)} budget records. Found {len(null_audits)} null actual_spend rows.")

        results = compute_growth(records, args.ward, args.category, args.growth_type)

        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        fieldnames = ["period", "ward", "category", "actual_spend", "growth_rate", "formula_used", "notes"]
        with open(args.output, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"Done. Results written to {args.output}")

    except ValueError as err:
        print(f"ERROR / REFUSAL: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
