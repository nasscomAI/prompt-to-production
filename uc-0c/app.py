"""
UC-0C — Number That Looks Right

Computes per-ward, per-category spend growth from the ward budget CSV, honoring
the enforcement rules in agents.md and the skill contracts in skills.md.

Three guards make the number trustworthy: it never aggregates across wards or
categories, it refuses to guess a growth type, and it flags every null
actual_spend (with its reason) instead of silently skipping it or treating it as
zero. Every output row shows the exact formula used.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
AGGREGATION_TOKENS = {"all", "*", "all wards", "all categories", "every", "total", "combined"}


def _norm_dash(s: str) -> str:
    """Normalise en/em dashes to a hyphen and collapse spaces so ward names match."""
    return " ".join(s.replace("–", "-").replace("—", "-").split()).lower()


def load_dataset(path: str):
    """Read the budget CSV, validate columns, and return (rows, null_report)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Input CSV missing required columns: {missing}")
        rows = list(reader)

    null_report = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"],
         "reason": (r["notes"].strip() or "no reason given")}
        for r in rows if r["actual_spend"].strip() == ""
    ]
    return rows, null_report


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Per-period growth table for ONE ward + ONE category. Refuses aggregation/guessing."""
    if not growth_type:
        raise ValueError("REFUSED: --growth-type not specified. Choose MoM or YoY — I will not guess.")
    gt = growth_type.upper()
    if gt not in ("MOM", "YOY"):
        raise ValueError(f"REFUSED: unknown growth-type '{growth_type}'. Use MoM or YoY.")
    if _norm_dash(ward) in AGGREGATION_TOKENS or _norm_dash(category) in AGGREGATION_TOKENS:
        raise ValueError("REFUSED: aggregation across wards/categories is not permitted. "
                         "Request one specific ward and one specific category.")

    sub = [r for r in rows
           if _norm_dash(r["ward"]) == _norm_dash(ward)
           and _norm_dash(r["category"]) == _norm_dash(category)]
    if not sub:
        raise ValueError(f"No rows for ward='{ward}', category='{category}'. Check exact names.")
    sub.sort(key=lambda r: r["period"])

    # Index spend by period for prior-period / prior-year lookups.
    spend = {r["period"]: r["actual_spend"].strip() for r in sub}

    def prior_key(period):
        y, m = period.split("-")
        if gt == "MOM":
            mm = int(m) - 1
            return f"{y}-{mm:02d}" if mm >= 1 else None
        return f"{int(y) - 1}-{m}"  # YoY

    table = []
    for r in sub:
        period = r["period"]
        cur = r["actual_spend"].strip()
        out = {"ward": r["ward"], "category": r["category"], "period": period,
               "budgeted_amount": r["budgeted_amount"], "actual_spend": cur or "NULL",
               "growth_type": gt, "formula": "", "growth_pct": "", "flag": ""}

        if cur == "":
            out["flag"] = f"NULL_INPUT: {r['notes'].strip() or 'no reason given'}"
            table.append(out); continue

        pk = prior_key(period)
        if pk is None:
            out["flag"] = "NO_PRIOR_PERIOD"
        elif pk not in spend:
            out["flag"] = "NO_PRIOR_YEAR_DATA" if gt == "YOY" else "NO_PRIOR_PERIOD"
        elif spend[pk] == "":
            out["flag"] = "NOT_COMPUTED: prior period null"
        else:
            prev = float(spend[pk]); cur_f = float(cur)
            pct = (cur_f - prev) / prev * 100 if prev != 0 else float("inf")
            out["formula"] = f"{gt} = ({cur_f} - {prev}) / {prev} * 100"
            out["growth_pct"] = f"{pct:+.1f}%"
        table.append(out)

    return table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward name (omit to run every ward)")
    parser.add_argument("--category", help="Exact category (omit to run every category)")
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement rule 4: refuse rather than guess a growth type.
    if not args.growth_type:
        print("REFUSED: --growth-type not specified. Re-run with --growth-type MoM or "
              "--growth-type YoY. I will not guess a default.")
        sys.exit(2)

    rows, null_report = load_dataset(args.input)
    print(f"Loaded {len(rows)} rows. Null actual_spend rows: {len(null_report)} (flagged, not skipped):")
    for n in null_report:
        print(f"  - {n['period']} | {n['ward']} | {n['category']} | {n['reason']}")

    # Enumerate the requested ward/category combinations — never aggregated.
    wards = [args.ward] if args.ward else sorted({r["ward"] for r in rows})
    cats = [args.category] if args.category else sorted({r["category"] for r in rows})

    fieldnames = ["ward", "category", "period", "budgeted_amount", "actual_spend",
                  "growth_type", "formula", "growth_pct", "flag"]
    all_rows = []
    try:
        for w in wards:
            for c in cats:
                all_rows.extend(compute_growth(rows, w, c, args.growth_type))
    except ValueError as exc:
        print(exc)
        sys.exit(2)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    n_flagged = sum(1 for r in all_rows if r["flag"].startswith("NULL_INPUT"))
    print(f"Wrote {len(all_rows)} rows ({len(wards)}×{len(cats)} ward/category combos), "
          f"{n_flagged} null rows flagged -> {args.output}")


if __name__ == "__main__":
    main()
