"""
UC-0C app.py — Ward Budget MoM Growth Analyzer

Computes month-over-month growth of actual spend for a single ward and
category, showing the formula per row, flagging null actual_spend rows,
and refusing cross-ward/cross-category aggregation or a missing growth type.

Enforcement (from agents.md):
  1. Never aggregate across wards or categories unless explicitly
     instructed — refuse if asked
  2. Flag every null row before computing; report the null reason from notes
  3. Show the formula used in every output row alongside the result
  4. If --growth-type is not specified — refuse and ask, never guess
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
ALLOWED_GROWTH_TYPES = ["MoM", "YoY"]


def norm(s):
    """Normalise dash characters so '–' and '-' match, and lower-case."""
    if s is None:
        return ""
    return s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2012", "-").strip().lower()


def load_dataset(input_path: str):
    """
    Read the ward budget CSV, validate columns, and report null
    actual_spend rows (with their notes) before returning.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
    except UnicodeDecodeError:
        with open(input_path, "r", encoding="latin-1", newline="") as f:
            rows = list(csv.DictReader(f))
    except OSError as exc:
        print(f"ERROR: cannot read input file {input_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print(f"ERROR: input file {input_path} has no data rows", file=sys.stderr)
        sys.exit(1)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing_cols:
        print(f"ERROR: input CSV missing required columns: {', '.join(missing_cols)}", file=sys.stderr)
        sys.exit(1)

    nulls = []
    for r in rows:
        spend = (r.get("actual_spend") or "").strip()
        if spend == "":
            nulls.append(
                {
                    "period": r["period"],
                    "ward": r["ward"],
                    "category": r["category"],
                    "notes": r.get("notes", "").strip(),
                }
            )

    if nulls:
        print(f"FLAG: {len(nulls)} row(s) have null actual_spend:")
        for n in nulls:
            print(f"  - {n['period']} | {n['ward']} | {n['category']} | note: {n['notes'] or 'not provided'}")
    else:
        print("FLAG: no null actual_spend rows found.")

    return rows


def compute_growth(rows: list):
    """
    Compute MoM growth per period for the filtered rows (single ward,
    single category), sorted by period. Returns a list of output rows.
    """
    ordered = sorted(rows, key=lambda r: r["period"])
    out_rows = []
    for i, r in enumerate(ordered):
        cur = (r.get("actual_spend") or "").strip()
        prev = (ordered[i - 1].get("actual_spend") or "").strip() if i > 0 else ""
        note = (r.get("notes") or "").strip()

        if cur == "":
            out_rows.append(
                {
                    "period": r["period"],
                    "ward": r["ward"],
                    "category": r["category"],
                    "actual_spend": "",
                    "previous_actual_spend": prev,
                    "growth_pct": "",
                    "formula": "",
                    "flag": "NULL_ACTUAL_SPEND",
                    "notes": note,
                }
            )
            continue

        if prev == "":
            out_rows.append(
                {
                    "period": r["period"],
                    "ward": r["ward"],
                    "category": r["category"],
                    "actual_spend": cur,
                    "previous_actual_spend": "",
                    "growth_pct": "",
                    "formula": "no previous month — growth not computed",
                    "flag": "",
                    "notes": note,
                }
            )
            continue

        cur_f = float(cur)
        prev_f = float(prev)
        growth = (cur_f - prev_f) / prev_f * 100
        out_rows.append(
            {
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "actual_spend": cur,
                "previous_actual_spend": prev,
                "growth_pct": f"{growth:.1f}",
                "formula": f"(({cur} - {prev}) / {prev}) * 100",
                "flag": "",
                "notes": note,
            }
        )
    return out_rows


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget MoM Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Budget category")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY — must be explicit, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Rule 4: growth type must be explicit.
    if not args.growth_type:
        print(
            "REFUSE: --growth-type is not specified. Specify MoM or YoY explicitly — never guess.",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.growth_type not in ALLOWED_GROWTH_TYPES:
        print(
            f"REFUSE: unknown growth type '{args.growth_type}'. Allowed values: MoM, YoY.",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.growth_type == "YoY":
        print(
            "REFUSE: YoY growth cannot be computed — the dataset covers a single year (2024).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Rule 1: no cross-ward / cross-category aggregation.
    if "all" in norm(args.ward) or "every" in norm(args.ward):
        print(
            "REFUSE: cross-ward aggregation is not permitted. Provide a single ward.",
            file=sys.stderr,
        )
        sys.exit(1)
    if "all" in norm(args.category) or "every" in norm(args.category):
        print(
            "REFUSE: cross-category aggregation is not permitted. Provide a single category.",
            file=sys.stderr,
        )
        sys.exit(1)

    rows = load_dataset(args.input)

    ward_norm, cat_norm = norm(args.ward), norm(args.category)
    available_wards = sorted({r["ward"] for r in rows})
    available_cats = sorted({r["category"] for r in rows})

    def resolve(target, candidates, label):
        exact = [c for c in candidates if norm(c) == target]
        if exact:
            return exact[0]
        partial = [c for c in candidates if target in norm(c)]
        if len(partial) == 1:
            return partial[0]
        return None

    ward = resolve(ward_norm, available_wards, "ward")
    if ward is None:
        print(f"REFUSE: ward '{args.ward}' not found in the dataset.", file=sys.stderr)
        print(f"  Available wards: {', '.join(available_wards)}", file=sys.stderr)
        sys.exit(1)

    category = resolve(cat_norm, available_cats, "category")
    if category is None:
        print(f"REFUSE: category '{args.category}' not found in the dataset.", file=sys.stderr)
        print(f"  Available categories: {', '.join(available_cats)}", file=sys.stderr)
        sys.exit(1)

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    print(f"Scope: ward='{ward}' | category='{category}' | growth-type=MoM | {len(filtered)} rows")

    out_rows = compute_growth(filtered)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "period", "ward", "category", "actual_spend",
                "previous_actual_spend", "growth_pct", "formula", "flag", "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"MoM growth written to {args.output} ({len(out_rows)} rows)")
    print("Formula used per row: ((current - previous) / previous) * 100")
    for o in out_rows:
        if o["growth_pct"]:
            print(f"  {o['period']}: {o['actual_spend']} vs {o['previous_actual_spend']} -> {o['growth_pct']}%")

    # Reference-value self-check for the documented demo case.
    if "kasba" in norm(ward) and "road" in norm(category):
        by_period = {o["period"]: o for o in out_rows}
        jul, oct_ = by_period.get("2024-07"), by_period.get("2024-10")
        if jul:
            expect_jul = "+33.1%" if jul["growth_pct"].startswith("33.1") else f"got {jul['growth_pct']}%"
            print(f"Reference check 2024-07: {jul['growth_pct']}% (expected +33.1%)")
        if oct_:
            expect_oct = "-34.8%" if oct_["growth_pct"].startswith("-34.8") else f"got {oct_['growth_pct']}%"
            print(f"Reference check 2024-10: {oct_['growth_pct']}% (expected -34.8%)")


if __name__ == "__main__":
    main()