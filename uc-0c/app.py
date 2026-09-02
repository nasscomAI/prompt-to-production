"""
UC-0C — Number That Looks Right

Computes period-over-period growth for exactly one ward and one category,
showing the arithmetic behind every figure and flagging every period it cannot
compute. It refuses rather than guesses: no scope, no growth type, no answer.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ["MoM", "YoY"]
# Rule 1 — values that ask for an aggregate rather than naming a scope.
AGGREGATE_REQUESTS = {"all", "all wards", "all categories", "*", "total", "everything"}


def load_dataset(csv_path: str):
    """Read the CSV, validate columns, and report every null before returning."""
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
    except OSError as exc:
        raise SystemExit(f"Cannot read input file {csv_path}: {exc}")

    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        raise SystemExit(f"Input file is missing required column(s): {', '.join(missing)}")

    parsed, nulls = [], []
    for r in rows:
        raw = (r.get("actual_spend") or "").strip()
        value = None
        if raw:
            try:
                value = float(raw)
            except ValueError:
                # Not coerced to zero: zero is a real spend value and would
                # corrupt every growth figure that touches it.
                value = None
        rec = {"period": r["period"].strip(), "ward": r["ward"].strip(),
               "category": r["category"].strip(), "actual_spend": value,
               "notes": (r.get("notes") or "").strip(),
               "raw_actual": raw}
        parsed.append(rec)
        if value is None:
            nulls.append({"period": rec["period"], "ward": rec["ward"],
                          "category": rec["category"],
                          "reason": rec["notes"] or "no reason given in notes column"})

    # Rule 2 — nulls are reported before anything is computed.
    print(f"Loaded {len(parsed)} rows. Null actual_spend: {len(nulls)}")
    for n in nulls:
        print(f"  NULL  {n['period']} · {n['ward']} · {n['category']} — {n['reason']}")
    return parsed, nulls


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Growth for exactly one ward and one category. Refuses rather than guesses."""
    if not growth_type:
        raise SystemExit(
            "Refusing to compute: --growth-type was not supplied. MoM and YoY answer "
            f"different questions and will not be guessed. Choose one of: {', '.join(GROWTH_TYPES)}.")
    if growth_type not in GROWTH_TYPES:
        raise SystemExit(f"Refusing to compute: unknown growth type '{growth_type}'. "
                         f"Choose one of: {', '.join(GROWTH_TYPES)}.")

    wards = sorted({r["ward"] for r in rows})
    cats = sorted({r["category"] for r in rows})
    for label, value, available in (("ward", ward, wards), ("category", category, cats)):
        if not value or value.strip().lower() in AGGREGATE_REQUESTS:
            raise SystemExit(
                f"Refusing to aggregate across {label}s. This tool reports one ward and one "
                f"category at a time; an all-{label} figure conceals the per-{label} movement "
                f"it averages. Available {label}s: {', '.join(available)}")
        if value not in available:
            raise SystemExit(f"Refusing to compute: {label} '{value}' is not in the dataset. "
                             f"Available {label}s: {', '.join(available)}")

    scoped = sorted([r for r in rows if r["ward"] == ward and r["category"] == category],
                    key=lambda r: r["period"])
    by_period = {r["period"]: r for r in scoped}

    out = []
    for r in scoped:
        period = r["period"]
        year, month = period.split("-")
        if growth_type == "MoM":
            m = int(month) - 1
            prev_key = f"{year}-{m:02d}" if m >= 1 else f"{int(year)-1}-12"
        else:
            prev_key = f"{int(year)-1}-{month}"
        prev = by_period.get(prev_key)

        row = {"period": period, "ward": ward, "category": category,
               "actual_spend": r["raw_actual"], "previous_period": prev_key,
               "previous_spend": prev["raw_actual"] if prev else "",
               "growth_type": growth_type, "growth_pct": "", "formula": "", "flag": ""}

        if r["actual_spend"] is None:
            row["flag"] = "NULL_ACTUAL — not computed"
            row["formula"] = f"not computed: actual_spend is null ({r['notes'] or 'no reason given'})"
        elif prev is None:
            row["flag"] = "NO_PRIOR_PERIOD — not computed"
            row["formula"] = (f"not computed: no {prev_key} row exists for this ward and category"
                              + (" (dataset covers a single year)" if growth_type == "YoY" else ""))
        elif prev["actual_spend"] is None:
            row["flag"] = "PRIOR_NULL — not computed"
            row["formula"] = (f"not computed: {prev_key} actual_spend is null "
                              f"({prev['notes'] or 'no reason given'}); the gap is not spanned")
        else:
            cur, pre = r["actual_spend"], prev["actual_spend"]
            pct = (cur - pre) / pre * 100
            row["growth_pct"] = f"{pct:+.1f}%"
            row["formula"] = f"({cur} - {pre}) / {pre} * 100 = {pct:+.1f}%"
        out.append(row)
    return out


def write_output(table, output_path: str):
    fields = ["period", "ward", "category", "actual_spend", "previous_period",
              "previous_spend", "growth_type", "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(table)
    computed = sum(1 for r in table if r["growth_pct"])
    flagged = sum(1 for r in table if r["flag"])
    print(f"Rows: {len(table)}  computed: {computed}  flagged: {flagged}")
    return {"rows": len(table), "computed": computed, "flagged": flagged}


def main():
    p = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    p.add_argument("--input", required=True, help="Path to ward_budget.csv")
    p.add_argument("--ward", help="Exactly one ward (required — no aggregation)")
    p.add_argument("--category", help="Exactly one category (required — no aggregation)")
    p.add_argument("--growth-type", dest="growth_type",
                   help="MoM or YoY — refused if omitted, never guessed")
    p.add_argument("--output", required=True, help="Path to write growth CSV")
    args = p.parse_args()

    rows, _ = load_dataset(args.input)
    table = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(table, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
