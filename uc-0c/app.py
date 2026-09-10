"""
UC-0C app.py — Number That Looks Right.
Implements load_dataset + compute_growth per skills.md, enforced by agents.md.
Run:
  python app.py --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
    --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
REFUSAL_AGG = (
    "REFUSED: aggregation across wards or categories is not permitted. "
    "Specify exactly one --ward and one --category (no 'All')."
)
REFUSAL_GROWTH = (
    "REFUSED: --growth-type is required (MoM or YoY). "
    "No formula was assumed; re-run with --growth-type MoM (or YoY)."
)


def load_dataset(input_path: str) -> list:
    """Read CSV, validate columns, report nulls, return row dicts."""
    try:
        with open(input_path, "r", newline="", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"No header found in {input_path}")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required columns {missing} in {input_path}")
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    nulls = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(nulls)}.")
    for r in nulls:
        print(
            f"  NULL: {r.get('period')} | {r.get('ward')} | {r.get('category')} "
            f"| reason: {r.get('notes', '').strip()}"
        )
    return rows


def _parse_float(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Return per-period table for one ward+category with formula shown."""
    if not ward or ward.strip().lower() in ("all", "all wards", "*"):
        raise ValueError(REFUSAL_AGG)
    if not category or category.strip().lower() in ("all", "all categories", "*"):
        raise ValueError(REFUSAL_AGG)
    if not growth_type or growth_type.strip().lower() not in ("mom", "yoy"):
        raise ValueError(REFUSAL_GROWTH)
    gt = growth_type.strip()
    gt_low = gt.lower()

    filtered = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    if not filtered:
        raise ValueError(f"No rows found for ward={ward!r} category={category!r}.")
    filtered.sort(key=lambda r: r.get("period", ""))

    # map period -> actual for YoY lookup
    actual_by_period = {r["period"]: _parse_float(r.get("actual_spend")) for r in filtered}
    out = []
    for i, r in enumerate(filtered):
        period = r.get("period", "")
        budgeted = (r.get("budgeted_amount") or "").strip()
        actual_raw = (r.get("actual_spend") or "").strip()
        actual = _parse_float(actual_raw)
        notes = (r.get("notes") or "").strip()

        prev = None
        formula = ""
        growth = ""
        note = ""
        if actual is None:
            note = f"NULL actual_spend flagged — not computed. Reason: {notes or 'not stated'}."
            formula = f"{gt}: not computed (current actual_spend is NULL)."
        else:
            if gt_low == "mom":
                prev = _parse_float(filtered[i - 1].get("actual_spend")) if i > 0 else None
                prev_period = filtered[i - 1].get("period") if i > 0 else None
                if prev is None:
                    formula = f"{gt}: not computed (previous period {'NULL' if i > 0 else 'none'})."
                    note = (
                        "First period or previous actual_spend NULL — no growth computed."
                        + (f" Prev reason: {(filtered[i-1].get('notes') or '').strip()}." if i > 0 and prev is None else "")
                    )
                else:
                    g = (actual - prev) / prev * 100 if prev != 0 else float("nan")
                    sign = "+" if g >= 0 else ""
                    growth = f"{sign}{g:.1f}%"
                    formula = f"{gt}: ({actual}-{prev})/{prev}*100 = {growth}"
            else:  # YoY — needs same month prior year; dataset is 2024-only
                y, m = period.split("-") if "-" in period else ("", "")
                prev_period = f"{int(y)-1:04d}-{m}" if y.isdigit() else None
                prev = actual_by_period.get(prev_period) if prev_period else None
                if prev is None:
                    formula = f"{gt}: N/A (no {prev_period} data in single-year dataset)."
                    note = "YoY not computable — prior-year data absent."
                else:
                    g = (actual - prev) / prev * 100 if prev != 0 else float("nan")
                    sign = "+" if g >= 0 else ""
                    growth = f"{sign}{g:.1f}%"
                    formula = f"{gt}: ({actual}-{prev})/{prev}*100 = {growth}"
        out.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_raw,
            "prev_actual_spend": ("" if prev is None else str(prev)),
            "growth_pct": growth,
            "formula": formula,
            "note": note,
        })
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C ward budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help="Exactly one ward")
    parser.add_argument("--category", required=False, default=None, help="Exactly one category")
    parser.add_argument("--growth-type", required=False, default=None, help="MoM or YoY (required)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        table = compute_growth(rows, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "period", "ward", "category", "budgeted_amount", "actual_spend",
            "prev_actual_spend", "growth_pct", "formula", "note",
        ])
        writer.writeheader()
        writer.writerows(table)
    print(f"Done. {len(table)} per-period rows written to {args.output}")


if __name__ == "__main__":
    main()
