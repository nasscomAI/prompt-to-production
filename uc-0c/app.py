"""
UC-0C app.py — Number That Looks Right
Built from agents.md (enforcement rules) and skills.md (skill contracts).
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend"}
VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(file_path: str) -> list:
    """
    Read the ward budget CSV, validate columns, and report null actual_spend
    rows before returning the parsed data.
    """
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        rows = []
        for raw in reader:
            actual_raw = (raw.get("actual_spend") or "").strip()
            rows.append({
                "period": raw["period"],
                "ward": raw["ward"],
                "category": raw["category"],
                "budgeted_amount": float(raw["budgeted_amount"]),
                "actual_spend": float(actual_raw) if actual_raw else None,
                "notes": (raw.get("notes") or "").strip(),
            })

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print(f"Null report: {len(null_rows)} row(s) with missing actual_spend:", file=sys.stderr)
    for r in null_rows:
        reason = r["notes"] or "no reason given in notes column"
        print(f"  - {r['period']} | {r['ward']} | {r['category']} | reason: {reason}", file=sys.stderr)

    return rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for exactly one ward+category. Refuses to guess
    on aggregation, missing growth_type, or missing actual_spend values.
    """
    if not ward or ward.strip().lower() in {"all", "*"}:
        return [{"flag": "REFUSED: no single ward specified — aggregation across wards is not permitted."}]
    if not category or category.strip().lower() in {"all", "*"}:
        return [{"flag": "REFUSED: no single category specified — aggregation across categories is not permitted."}]
    if not growth_type or growth_type not in VALID_GROWTH_TYPES:
        return [{"flag": f"REFUSED: --growth-type must be one of {sorted(VALID_GROWTH_TYPES)} — not specified or guessed."}]

    matching = [r for r in rows if r["ward"] == ward and r["category"] == category]
    matching.sort(key=lambda r: r["period"])

    if not matching:
        return [{"flag": f"REFUSED: no rows found for ward='{ward}' category='{category}'."}]

    results = []
    for i, row in enumerate(matching):
        period, actual = row["period"], row["actual_spend"]

        if actual is None:
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": "", "growth_type": growth_type,
                "growth_pct": "", "formula": "N/A",
                "flag": f"NULL — not computed. Reason: {row['notes'] or 'no reason given'}",
            })
            continue

        if growth_type == "YoY":
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": actual, "growth_type": growth_type,
                "growth_pct": "", "formula": "N/A",
                "flag": "NULL — dataset covers only 2024; no prior-year data available for YoY.",
            })
            continue

        # MoM
        if i == 0:
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": actual, "growth_type": growth_type,
                "growth_pct": "", "formula": "N/A",
                "flag": "No prior period available for MoM growth.",
            })
            continue

        previous = matching[i - 1]["actual_spend"]
        if previous is None:
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": actual, "growth_type": growth_type,
                "growth_pct": "", "formula": "N/A",
                "flag": f"Prior period ({matching[i - 1]['period']}) has null actual_spend — growth not computed.",
            })
            continue

        growth_pct = (actual - previous) / previous * 100
        formula = f"({actual} - {previous}) / {previous} * 100 = {growth_pct:.1f}%"
        results.append({
            "period": period, "ward": ward, "category": category,
            "actual_spend": actual, "growth_type": growth_type,
            "growth_pct": f"{growth_pct:.1f}", "formula": formula,
            "flag": "",
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default=None, help="Exact ward name, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", default=None, help="Exact category name")
    parser.add_argument("--growth-type", dest="growth_type", default=None, choices=["MoM", "YoY"],
                         help="Growth type — must be explicitly specified")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_type", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    print(f"Done. {len(results)} row(s) written to {args.output}")


if __name__ == "__main__":
    main()
