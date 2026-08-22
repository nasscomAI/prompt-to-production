"""
UC-0C app.py
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys


def load_dataset(input_path: str) -> list:
    """
    Reads the CSV, validates expected columns, and reports null rows
    before returning the data.
    """
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
        if not expected_cols.issubset(set(reader.fieldnames)):
            missing = expected_cols - set(reader.fieldnames)
            raise ValueError(f"Missing expected columns: {missing}")
        rows = list(reader)

    null_rows = [r for r in rows if r["actual_spend"] == "" or r["actual_spend"] is None]
    if null_rows:
        print(f"[NULL CHECK] Found {len(null_rows)} rows with null actual_spend:")
        for r in null_rows:
            print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes']}")

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes MoM or YoY growth for exactly one ward+category pair.
    Refuses to aggregate across wards/categories.
    Flags nulls instead of computing around them.
    Shows the formula used per row.
    """
    filtered = [
        r for r in rows
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError(f"No data found for ward='{ward}' and category='{category}'. Check exact spelling against the dataset.")

    filtered.sort(key=lambda r: r["period"])

    results = []
    for i, row in enumerate(filtered):
        period = row["period"]
        actual_spend_raw = row["actual_spend"]

        if actual_spend_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "NULL",
                "growth_pct": "NULL - FLAGGED",
                "formula_used": "N/A - actual_spend is null",
                "null_reason": row["notes"]
            })
            continue

        actual_spend = float(actual_spend_raw)

        if growth_type == "MoM":
            compare_index = i - 1
        elif growth_type == "YoY":
            compare_index = i - 12
        else:
            raise ValueError(f"Unsupported growth_type: {growth_type}")

        if compare_index < 0 or compare_index >= len(filtered):
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "growth_pct": "N/A - insufficient prior period data",
                "formula_used": f"{growth_type} requires a prior period not available in range",
                "null_reason": ""
            })
            continue

        prior_raw = filtered[compare_index]["actual_spend"]
        if prior_raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual_spend,
                "growth_pct": "NULL - FLAGGED (prior period is null)",
                "formula_used": "Cannot compute — comparison period has null actual_spend",
                "null_reason": filtered[compare_index]["notes"]
            })
            continue

        prior = float(prior_raw)
        growth_pct = ((actual_spend - prior) / prior) * 100 if prior != 0 else "N/A (prior=0)"
        formula_str = f"({actual_spend} - {prior}) / {prior} * 100"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_spend,
            "growth_pct": round(growth_pct, 1) if isinstance(growth_pct, float) else growth_pct,
            "formula_used": formula_str,
            "null_reason": ""
        })

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", required=False)
    parser.add_argument("--category", required=False)
    parser.add_argument("--growth-type", required=False, dest="growth_type")
    args = parser.parse_args()

    # --- ENFORCEMENT: refuse instead of guessing scope ---
    if not args.ward or not args.category:
        print("[REFUSED] This tool requires an explicit --ward and --category. "
              "It will not aggregate across wards or categories. Please specify both.")
        sys.exit(1)

    if not args.growth_type:
        print("[REFUSED] --growth-type is required (MoM or YoY). "
              "This tool will not guess which growth calculation you want.")
        sys.exit(1)

    if args.growth_type not in {"MoM", "YoY"}:
        print(f"[REFUSED] Invalid --growth-type '{args.growth_type}'. Must be exactly 'MoM' or 'YoY'.")
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth_pct", "formula_used", "null_reason"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()