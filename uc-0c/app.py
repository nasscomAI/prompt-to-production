"""
UC-0C app.py — Budget growth calculator.
Implements agents.md enforcement via the skills.md workflow:
load_dataset -> compute_growth -> per-ward per-category CSV output.

Refuses (instead of guessing) when ward/category/growth-type is missing
or when cross-ward or cross-category aggregation is requested.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]

AGGREGATION_WORDS = {"all", "*", "total", "every", "combined"}


def refuse(message):
    """Refuse an underspecified or out-of-scope request — never guess."""
    print(f"REFUSED: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_dataset(input_path):
    """Read CSV, validate columns, report null actual_spend rows."""
    try:
        f = open(input_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        refuse(f"input file not found: {input_path}")
    with f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            refuse(f"input file has no header row: {input_path}")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            refuse(f"input is missing required columns {missing}; "
                   f"expected {REQUIRED_COLUMNS}")
        rows = list(reader)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print(f"Loaded {len(rows)} rows from {input_path}.")
    print(f"Found {len(null_rows)} null actual_spend rows:")
    for r in null_rows:
        print(f"  NULL {r.get('period')} | {r.get('ward')} | "
              f"{r.get('category')} | reason: {r.get('notes')}")
    return rows


def _parse_actual(value):
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def compute_growth(rows, ward, category, growth_type):
    """Per-period growth table for one ward + one category."""
    if not ward or not ward.strip():
        refuse("missing --ward. Specify exactly one ward (no aggregation).")
    if not category or not category.strip():
        refuse("missing --category. Specify exactly one category.")
    if not growth_type or not growth_type.strip():
        refuse("missing --growth-type. Specify MoM or YoY — will not guess.")
    if growth_type not in ("MoM", "YoY"):
        refuse(f"unknown --growth-type '{growth_type}'. Choose MoM or YoY.")
    if ward.strip().lower() in AGGREGATION_WORDS or category.strip().lower() in AGGREGATION_WORDS:
        refuse("cross-ward / cross-category aggregation is not allowed. "
               "Request exactly one ward and one category.")

    scoped = [r for r in rows
              if r.get("ward") == ward and r.get("category") == category]
    if not scoped:
        wards = sorted({r.get("ward") for r in rows})
        cats = sorted({r.get("category") for r in rows})
        refuse(f"no data for ward '{ward}' + category '{category}'. "
               f"Known wards: {wards}. Known categories: {cats}.")
    scoped.sort(key=lambda r: r.get("period") or "")

    actuals = [(r, _parse_actual(r.get("actual_spend"))) for r in scoped]
    # A value that looks present but is unparseable is also a null-equivalent.
    for r, v in actuals:
        if (r.get("actual_spend") or "").strip() and v is None:
            print(f"WARNING: unparseable actual_spend "
                  f"'{r.get('actual_spend')}' at {r.get('period')} — "
                  f"treated as null.", file=sys.stderr)

    out = []
    for i, (row, val) in enumerate(actuals):
        period = row.get("period")
        budgeted = (row.get("budgeted_amount") or "").strip()
        actual_txt = (row.get("actual_spend") or "").strip()
        growth = ""
        formula = ""
        flag = ""

        if val is None:
            reason = (row.get("notes") or "").strip() or "actual_spend is null"
            flag = f"NULL actual_spend — {reason}; growth not computed"
        elif growth_type == "MoM":
            if i == 0:
                flag = "First period — no prior month; growth not computed"
            else:
                prev_val = actuals[i - 1][1]
                prev_period = scoped[i - 1].get("period")
                if prev_val is None:
                    prev_reason = (scoped[i - 1].get("notes") or "").strip()
                    flag = (f"Prior period {prev_period} actual is null "
                            f"({prev_reason}); growth not computed")
                elif prev_val == 0:
                    flag = (f"Prior period {prev_period} actual is zero; "
                            f"growth undefined, not computed")
                else:
                    g = (val - prev_val) / prev_val * 100
                    growth = f"{g:+.1f}%"
                    formula = (f"MoM: ({val} - {prev_val}) / {prev_val} x 100")
        else:  # YoY
            year, month = period.split("-")[0], period.split("-")[1]
            prior_period = f"{int(year) - 1:04d}-{month}"
            prior = next((v for r2, v in actuals
                          if r2.get("period") == prior_period), None)
            # None here means "no such row" OR "row was null" — flag either way.
            if prior is None:
                prior_rows = [r2 for r2 in scoped
                              if r2.get("period") == prior_period]
                if prior_rows:
                    prior_reason = (prior_rows[0].get("notes") or "").strip()
                    flag = (f"Prior-year period {prior_period} actual is null "
                            f"({prior_reason}); growth not computed")
                else:
                    flag = (f"No prior-year data for {prior_period}; "
                            f"YoY growth not computed")
            elif prior == 0:
                flag = (f"Prior-year period {prior_period} actual is zero; "
                        f"growth undefined, not computed")
            else:
                g = (val - prior) / prior * 100
                growth = f"{g:+.1f}%"
                formula = f"YoY: ({val} - {prior}) / {prior} x 100"

        if growth and not formula:
            formula = growth_type  # safety net; should be unreachable
        out.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted,
            "actual_spend": actual_txt,
            "growth_pct": growth,
            "formula": formula,
            "flag": flag,
        })
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None,
                        help="Exactly one ward (refuses aggregation)")
    parser.add_argument("--category", required=False, default=None,
                        help="Exactly one category")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="MoM or YoY (required — never guessed)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args(argv)

    rows = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount",
                  "actual_spend", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)

    computed = sum(1 for r in table if r["growth_pct"])
    flagged = sum(1 for r in table if r["flag"])
    print(f"Wrote {len(table)} per-period rows to {args.output} "
          f"({computed} growth values computed, {flagged} rows flagged).")


if __name__ == "__main__":
    main()
