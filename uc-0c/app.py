"""
UC-0C — Number That Looks Right
Computes per-ward per-category growth rates (MoM/YoY) with null flagging,
formula transparency, and strict scope enforcement.
"""
import argparse
import csv
import sys


def load_dataset(input_path: str) -> tuple:
    """
    Read ward budget CSV, validate columns, report nulls.
    Returns (rows, null_report).
    """
    try:
        with open(input_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if rows:
        actual_cols = set(rows[0].keys())
        missing = required - actual_cols
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    else:
        raise ValueError("Dataset has zero data rows.")

    null_report = []
    for row in rows:
        spend = row.get("actual_spend", "").strip()
        if spend == "":
            null_report.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "").strip() or "No reason provided"
            })

    print(f"Dataset loaded: {len(rows)} rows.")
    print(f"NULL actual_spend rows found: {len(null_report)}")
    for nr in null_report:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}")
    print()

    return rows, null_report


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute growth for a specific ward + category.
    Returns list of output dicts with formula shown per row.
    """
    all_wards = sorted(set(r["ward"] for r in rows))
    all_categories = sorted(set(r["category"] for r in rows))

    if ward not in all_wards:
        raise ValueError(f"Ward '{ward}' not found. Available: {all_wards}")
    if category not in all_categories:
        raise ValueError(f"Category '{category}' not found. Available: {all_categories}")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be MoM or YoY.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        raise ValueError(f"No data found for ward='{ward}', category='{category}'.")

    results = []
    period_map = {r["period"]: r for r in filtered}

    for i, row in enumerate(filtered):
        period = row["period"]
        spend_str = row["actual_spend"].strip()
        notes = row.get("notes", "").strip()

        # Determine previous period based on growth type
        if growth_type == "MoM":
            prev_idx = i - 1
            prev_row = filtered[prev_idx] if prev_idx >= 0 else None
        else:  # YoY
            year, month = period.split("-")
            prev_period = f"{int(year) - 1}-{month}"
            prev_row = period_map.get(prev_period)

        # Current value
        if spend_str == "":
            current_val = None
        else:
            current_val = float(spend_str)

        # Previous value
        prev_val = None
        prev_spend_str = ""
        if prev_row:
            prev_spend_str = prev_row["actual_spend"].strip()
            if prev_spend_str != "":
                prev_val = float(prev_spend_str)

        # Build output row
        out = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": spend_str if spend_str else "NULL",
            "previous_actual_spend": prev_spend_str if prev_row and prev_spend_str else ("NULL" if prev_row else "N/A"),
            "growth_pct": "",
            "formula": "",
            "flag": ""
        }

        if current_val is None:
            out["growth_pct"] = "NULL"
            out["formula"] = "N/A — actual_spend is null"
            out["flag"] = f"NULL: {notes}" if notes else "NULL: No reason provided"
        elif prev_row is None:
            out["growth_pct"] = "N/A"
            out["formula"] = "N/A (first period)"
            out["flag"] = ""
        elif prev_val is None:
            out["growth_pct"] = "NULL"
            out["formula"] = "N/A — previous actual_spend is null"
            prev_notes = prev_row.get("notes", "").strip()
            out["flag"] = f"PREV_NULL: {prev_notes}" if prev_notes else "PREV_NULL: No reason provided"
        elif prev_val == 0:
            out["growth_pct"] = "INF"
            out["formula"] = f"({current_val} - 0) / 0 = undefined"
            out["flag"] = "DIVISION_BY_ZERO: previous spend is 0"
        else:
            growth = round(((current_val - prev_val) / prev_val) * 100, 1)
            out["growth_pct"] = f"{growth:+.1f}%"
            out["formula"] = f"(({current_val} - {prev_val}) / {prev_val}) * 100 = {growth:.1f}%"
            out["flag"] = ""

        results.append(out)

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match)")
    parser.add_argument("--category", required=True, help="Category name (exact match)")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output", required=True, help="Path to write output CSV")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend",
                  "previous_actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for r in results if r["flag"])
    print(f"Computed {args.growth_type} growth for: {args.ward} | {args.category}")
    print(f"Output rows: {len(results)} | Flagged: {flagged}")
    print(f"Written to: {args.output}")


if __name__ == "__main__":
    main()
