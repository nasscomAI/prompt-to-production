"""
UC-0C — Number That Looks Right
Computes per-ward, per-category growth from the ward budget CSV per the
enforcement rules in agents.md and skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend"]
SUPPORTED_GROWTH = {"MoM"}


def load_dataset(path: str) -> tuple:
    """Read the CSV, validate columns, and report null rows before computing."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError(f"Dataset missing required columns: {', '.join(missing)}")

    null_rows = [
        r for r in rows
        if r.get("actual_spend") is None or str(r.get("actual_spend")).strip() == ""
    ]
    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Return per-period growth rows for one ward + category."""
    sub = [r for r in rows if r["ward"] == ward and r["category"] == category]
    sub.sort(key=lambda r: r["period"])

    formula = "(A[t] - A[t-1]) / A[t-1] * 100"
    if growth_type == "MoM":
        formula = "MoM = (A[t] - A[t-1]) / A[t-1] * 100"

    out = []
    prev = None
    for r in sub:
        spend_raw = str(r["actual_spend"]).strip()
        if spend_raw == "":
            out.append({
                "period": r["period"],
                "ward": ward,
                "category": category,
                "budgeted_amount": r["budgeted_amount"],
                "actual_spend": "",
                "growth_type": growth_type,
                "formula": formula,
                "growth_pct": "",
                "null_flag": "YES",
                "notes": r.get("notes", "").strip(),
            })
            prev = None
            continue
        spend = float(spend_raw)
        growth = "" if prev is None else round((spend - prev) / prev * 100, 1)
        out.append({
            "period": r["period"],
            "ward": ward,
            "category": category,
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": spend,
            "growth_type": growth_type,
            "formula": formula,
            "growth_pct": growth,
            "null_flag": "",
            "notes": r.get("notes", "").strip(),
        })
        prev = spend
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exactly one ward, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", required=True, help="Exactly one category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.ward.strip():
        sys.exit("REFUSE: --ward is required. All-ward aggregation is not permitted.")
    if not args.category.strip():
        sys.exit("REFUSE: --category is required. All-category aggregation is not permitted.")
    if args.growth_type not in SUPPORTED_GROWTH:
        sys.exit(f"REFUSE: unsupported growth-type '{args.growth_type}'. Supported: {', '.join(sorted(SUPPORTED_GROWTH))}. Never guess the formula.")

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Dataset loaded: {len(rows)} rows. Null actual_spend rows: {len(null_rows)}")
        for r in null_rows:
            print(f"  NULL {r['period']} {r['ward']} {r['category']} - reason: {r.get('notes','').strip() or '(none given)'}")

    if not any(r["ward"] == args.ward for r in rows):
        sys.exit(f"REFUSE: ward '{args.ward}' not found in dataset.")
    if not any(r["category"] == args.category for r in rows):
        sys.exit(f"REFUSE: category '{args.category}' not found in dataset.")

    out = compute_growth(rows, args.ward, args.category, args.growth_type)
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "growth_type", "formula", "growth_pct", "null_flag", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out)

    print(f"Done. Per-ward per-category growth written to {args.output} ({len(out)} period rows)")


if __name__ == "__main__":
    main()
