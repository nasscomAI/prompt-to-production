"""
UC-0C — Number That Looks Right
Built per agents.md (RICE enforcement rules) and skills.md.
"""
import argparse
import csv
import sys


def load_dataset(file_path: str) -> list:
    """
    Read the budget CSV, validate columns, report null rows before returning.
    """
    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    rows = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required column(s): {sorted(missing)}")
        for row in reader:
            actual = row["actual_spend"].strip()
            row["actual_spend"] = float(actual) if actual else None
            row["budgeted_amount"] = float(row["budgeted_amount"])
            rows.append(row)

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"load_dataset: {len(rows)} rows loaded, {len(null_rows)} null actual_spend row(s):", file=sys.stderr)
    for r in null_rows:
        print(f"  {r['period']} | {r['ward']} | {r['category']} | reason: {r['notes'] or '(no reason given)'}", file=sys.stderr)
    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Per-period growth table for ONE ward+category. Refuses on missing/ALL scope.
    """
    if not ward or ward.strip().upper() == "ALL":
        raise ValueError("Refusing: all-ward aggregation is not allowed. Specify a single ward.")
    if not category or category.strip().upper() == "ALL":
        raise ValueError("Refusing: all-category aggregation is not allowed. Specify a single category.")
    if not growth_type:
        raise ValueError("Refusing: --growth-type not specified. Specify MoM or YoY — never guessed.")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"Refusing: unknown growth-type '{growth_type}'. Must be MoM or YoY.")

    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    subset.sort(key=lambda r: r["period"])
    lag = 1 if growth_type == "MoM" else 12

    out = []
    for i, row in enumerate(subset):
        period = row["period"]
        actual = row["actual_spend"]

        if actual is None:
            out.append({
                "period": period,
                "actual_spend": "NULL",
                "formula": "not computed",
                "growth_percent": "NA",
                "flag": f"NULL_FLAG: {row['notes'] or 'no reason given'}",
            })
            continue

        prior_idx = i - lag
        if prior_idx < 0 or subset[prior_idx]["actual_spend"] is None:
            out.append({
                "period": period,
                "actual_spend": actual,
                "formula": "not computed",
                "growth_percent": "NA",
                "flag": "no comparable prior period" if prior_idx >= 0 else "insufficient history",
            })
            continue

        prior = subset[prior_idx]["actual_spend"]
        growth = (actual - prior) / prior * 100
        out.append({
            "period": period,
            "actual_spend": actual,
            "formula": f"({actual}-{prior})/{prior}*100",
            "growth_percent": round(growth, 1),
            "flag": "",
        })

    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name")
    parser.add_argument("--category", required=True, help="Single category name")
    parser.add_argument("--growth-type", required=True, choices=["MoM", "YoY"], help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "actual_spend", "formula", "growth_percent", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Done. {len(result)} periods written to {args.output}")
