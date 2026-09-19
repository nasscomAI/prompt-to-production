"""UC-0C - Ward budget growth calculator (per ward, per category)"""
import argparse
import csv
import re
import sys

REQUIRED_COLS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
ALL_WORDS = {"all", "*", "any", "all wards", "all categories"}


def norm(s: str) -> str:
    """Normalise dashes/spaces/case so 'Ward 1 – Kasba' and 'Ward 1 - Kasba' match."""
    s = re.sub(r"[\u2010-\u2015\u2212]", "-", s or "")
    s = re.sub(r"\s*-\s*", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def refuse(msg: str):
    print(f"REFUSED: {msg}", file=sys.stderr)
    sys.exit(1)


def load_dataset(path: str) -> list:
    """Read CSV, validate columns, report null actual_spend rows before returning."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
            if missing:
                refuse(f"Input is missing required columns: {', '.join(missing)}")
            rows = list(reader)
    except OSError as e:
        refuse(f"Cannot read input file: {e}")
    nulls = [r for r in rows if (r["actual_spend"] or "").strip() == ""]
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(nulls)}")
    for r in nulls:
        print(f"  NULL: {r['period']} | {r['ward']} | {r['category']} | reason: {(r['notes'] or '').strip() or 'not given'}")
    return rows


def pick(rows, ward, category):
    wards = sorted({r["ward"] for r in rows})
    cats = sorted({r["category"] for r in rows})
    if norm(ward) in ALL_WORDS or norm(category) in ALL_WORDS:
        refuse("Aggregating across wards or categories is not allowed. Give one ward and one category.")
    w = [x for x in wards if norm(x) == norm(ward)] or [x for x in wards if norm(ward) and norm(ward) in norm(x)]
    c = [x for x in cats if norm(x) == norm(category)] or [x for x in cats if norm(category) and norm(category) in norm(x)]
    if len(w) != 1:
        refuse(f"Ward '{ward}' not found or ambiguous. Valid wards: {wards}")
    if len(c) != 1:
        refuse(f"Category '{category}' not found or ambiguous. Valid categories: {cats}")
    sel = [r for r in rows if r["ward"] == w[0] and r["category"] == c[0]]
    return w[0], c[0], sorted(sel, key=lambda r: r["period"])


def compute_growth(rows, ward, category, growth_type) -> list:
    """Per-period table for ONE ward + category, with the formula shown on every row."""
    ward, category, sel = pick(rows, ward, category)
    by_period = {r["period"]: r for r in sel}
    out = []
    for r in sel:
        period = r["period"]
        raw = (r["actual_spend"] or "").strip()
        cur = float(raw) if raw else None
        y, m = map(int, period.split("-"))
        if growth_type == "MoM":
            prev_period = f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"
        else:
            prev_period = f"{y - 1}-{m:02d}"
        prev_row = by_period.get(prev_period)
        prev_raw = (prev_row["actual_spend"] or "").strip() if prev_row else None
        prev = float(prev_raw) if prev_raw else None
        growth, flag = "", ""
        formula = f"{growth_type} = (actual_spend[{period}] - actual_spend[{prev_period}]) / actual_spend[{prev_period}] * 100"
        if cur is None:
            flag = f"NULL actual_spend - not computed. Reason: {(r['notes'] or '').strip() or 'not given'}"
        elif prev_row is None:
            flag = f"No {prev_period} data in dataset - not computed"
        elif prev is None:
            flag = f"Previous period {prev_period} is NULL - not computed"
        elif prev == 0:
            flag = f"Previous period {prev_period} is zero - not computed"
        else:
            growth = f"{(cur - prev) / prev * 100:+.1f}%"
        out.append({"period": period, "ward": ward, "category": category,
                    "actual_spend": raw, "growth_type": growth_type,
                    "growth": growth, "formula": formula, "flag": flag})
    return out


def main():
    p = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    p.add_argument("--input", required=True)
    p.add_argument("--ward", help="Exact ward name (one ward only)")
    p.add_argument("--category", help="Exact category name (one category only)")
    p.add_argument("--growth-type", help="MoM or YoY (required, never guessed)")
    p.add_argument("--output", required=True)
    a = p.parse_args()
    if not a.growth_type or a.growth_type not in GROWTH_TYPES:
        refuse("--growth-type is required and must be MoM or YoY. Not guessing. Please specify which one.")
    if not a.ward or not a.category:
        refuse("--ward and --category are both required. Aggregating across wards or categories is not allowed.")
    rows = load_dataset(a.input)
    table = compute_growth(rows, a.ward, a.category, a.growth_type)
    cols = ["period", "ward", "category", "actual_spend", "growth_type", "growth", "formula", "flag"]
    with open(a.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(table)
    print(f"Done. Growth table written to {a.output}")


if __name__ == "__main__":
    main()