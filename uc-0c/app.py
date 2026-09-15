"""
UC-0C app.py — Number That Looks Right
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import csv
import sys


def load_dataset(path: str) -> list:
    """
    Reads the ward budget CSV, validates required columns, and reports
    null count and which rows before returning the parsed data.
    Returns a list of dicts with actual_spend as float or None.
    """
    required_columns = {"period", "ward", "category", "budgeted_amount",
                         "actual_spend", "notes"}

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            raise ValueError(f"Input CSV is missing required columns: {missing}")

        rows = []
        null_rows = []
        for row in reader:
            actual_raw = (row.get("actual_spend") or "").strip()
            actual = float(actual_raw) if actual_raw else None
            row["actual_spend"] = actual
            row["budgeted_amount"] = float(row["budgeted_amount"])
            rows.append(row)
            if actual is None:
                null_rows.append(row)

    print(f"Loaded {len(rows)} rows. Found {len(null_rows)} null actual_spend rows:")
    for r in null_rows:
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'] or '(no reason given)'}")

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Filters to a single ward + category, computes per-period growth
    (MoM or YoY), and returns a list of result dicts, each showing the
    formula used. Null periods are flagged rather than computed, and
    periods whose comparison base is null are also flagged.
    """
    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not subset:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'. "
            f"Check exact spelling/spacing against the source CSV."
        )

    subset.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in subset}
    periods = [r["period"] for r in subset]

    results = []
    for i, period in enumerate(periods):
        current = by_period[period]
        current_val = current["actual_spend"]

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period, "ward": ward, "category": category,
                    "actual_spend": current_val, "growth_type": growth_type,
                    "growth_pct": "", "formula": "N/A — no prior month in dataset",
                    "flag": "",
                })
                continue
            prior_period = periods[i - 1]
            prior_val = by_period[prior_period]["actual_spend"]

        elif growth_type == "YoY":
            # Data only covers Jan–Dec 2024, so no prior-year data exists.
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": current_val, "growth_type": growth_type,
                "growth_pct": "", "formula": "N/A — dataset has no prior-year data for YoY",
                "flag": "INSUFFICIENT_HISTORY",
            })
            continue
        else:
            raise ValueError(f"Unsupported growth_type: {growth_type}")

        if current_val is None or prior_val is None:
            missing_side = "current" if current_val is None else "prior"
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": current_val if current_val is not None else "",
                "growth_type": growth_type, "growth_pct": "",
                "formula": f"Not computed — {missing_side} period value is null",
                "flag": "NULL_NOT_COMPUTED",
            })
            continue

        growth_pct = ((current_val - prior_val) / prior_val) * 100
        formula = f"({current_val} - {prior_val}) / {prior_val} * 100 = {growth_pct:.1f}%"

        results.append({
            "period": period, "ward": ward, "category": category,
            "actual_spend": current_val, "growth_type": growth_type,
            "growth_pct": f"{growth_pct:.1f}", "formula": formula,
            "flag": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"],
                         help="Growth type — must be explicitly specified, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refuse any attempt at cross-ward or cross-category aggregation.
    if args.ward.strip().lower() in ("all", "all wards", "*"):
        print("REFUSED: This tool computes growth for a single ward only. "
              "Aggregating across all wards is not permitted.")
        sys.exit(1)
    if args.category.strip().lower() in ("all", "all categories", "*"):
        print("REFUSED: This tool computes growth for a single category only. "
              "Aggregating across all categories is not permitted.")
        sys.exit(1)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend",
                  "growth_type", "growth_pct", "formula", "flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} periods written to {args.output}")


if __name__ == "__main__":
    main()