"""
UC-0C app.py — Number That Looks Right

Run:
  python app.py --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
    --growth-type MoM --output growth_output.csv
"""
import argparse
import csv


REQUIRED_COLS = ["period", "ward", "category", "budgeted_amount", "actual_spend"]


def load_dataset(path: str):
    """Read CSV, validate columns, separate null actual_spend rows."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        rows = list(reader)

    nulls = []
    clean = []
    for r in rows:
        spend = (r.get("actual_spend") or "").strip()
        if spend == "":
            nulls.append(r)
        else:
            r["actual_spend"] = float(spend)
            r["budgeted_amount"] = float(r["budgeted_amount"])
            clean.append(r)
    print(f"Loaded {len(rows)} rows. {len(nulls)} null actual_spend rows flagged.")
    return {"rows": clean, "nulls": nulls}


def compute_growth(dataset, ward, category, growth_type):
    """Per-period growth table for one ward + category."""
    if not growth_type:
        raise ValueError("REFUSE: --growth-type is required (MoM or YoY). Will not guess.")
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(f"REFUSE: unsupported growth-type '{growth_type}'. Use MoM or YoY.")

    subset = sorted(
        [r for r in dataset["rows"]
         if r["ward"] == ward and r["category"] == category],
        key=lambda r: r["period"],
    )
    if not subset:
        raise ValueError(f"REFUSE: no data for ward='{ward}' category='{category}'.")

    results = []
    for i, r in enumerate(subset):
        period = r["period"]
        cur = r["actual_spend"]
        prev = None
        if growth_type == "MoM" and i > 0:
            prev = subset[i - 1]["actual_spend"]
        elif growth_type == "YoY" and i >= 12:
            prev = subset[i - 12]["actual_spend"]

        if prev is not None and prev != 0:
            growth = (cur - prev) / prev * 100
            formula = f"({growth_type}) = (actual_t - actual_t-1)/actual_t-1 * 100"
            growth_str = f"{growth:+.1f}%"
        else:
            formula = f"({growth_type}) = no prior period available"
            growth_str = "n/a"

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{r['budgeted_amount']:.1f}",
            "actual_spend": f"{cur:.1f}",
            "formula": formula,
            "growth_pct": growth_str,
        })

    # Append null rows for this ward/category if any.
    for n in dataset["nulls"]:
        if n["ward"] == ward and n["category"] == category:
            results.append({
                "period": n["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": n["budgeted_amount"],
                "actual_spend": "NULL",
                "formula": "(null) actual_spend missing — not computed",
                "growth_pct": f"NULL: {n.get('notes','').strip()}",
            })
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, dest="growth_type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    table = compute_growth(dataset, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount",
                  "actual_spend", "formula", "growth_pct"]
    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)
    print(f"Growth table written to {args.output} ({len(table)} rows)")


if __name__ == "__main__":
    main()
