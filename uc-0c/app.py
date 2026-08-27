"""
UC-0C — Number That Looks Right

Computes ward-level / category-level budget growth without the three failure modes:
  - Wrong aggregation level -> refuses any all-ward / all-category request
  - Silent null handling     -> reports all NULL actual_spend rows (with reasons)
                                BEFORE computing, and never computes across a NULL
  - Formula assumption       -> --growth-type is mandatory (MoM or YoY); the formula
                                string is written into every output row

Run:
  python app.py --input ../data/budget/ward_budget.csv \
                --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
                --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

# Ward names contain an en-dash and formulas use ×/→; force UTF-8 stdout so the
# tool runs on Windows consoles (cp1252) too.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

VALID_GROWTH = {"MoM", "YoY"}
FORMULAS = {
    "MoM": "MoM = (current - prior_month) / prior_month × 100",
    "YoY": "YoY = (current - same_month_prior_year) / same_month_prior_year × 100",
}
OUT_FIELDS = ["period", "ward", "category", "actual_spend",
              "growth_percentage", "formula_applied", "null_flag_reason"]


def _refuse(message: str):
    print(f"REFUSED: {message}", file=sys.stderr)
    sys.exit(2)


def load_dataset(input_path: str):
    """
    Read the CSV, validate columns, and report every NULL actual_spend row with its
    notes reason BEFORE any computation. Returns (rows, null_rows).
    """
    required = {"period", "ward", "category", "budgeted_amount",
                "actual_spend", "notes"}
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = required - set(reader.fieldnames or [])
        if missing:
            _refuse(f"input missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print(f"NULL CHECK: {len(null_rows)} row(s) have a missing actual_spend "
          f"(reported before computing):")
    for r in null_rows:
        reason = (r.get("notes") or "").strip() or "(no reason given in notes)"
        print(f"  - {r['period']} · {r['ward']} · {r['category']} → {reason}")
    print()
    return rows, null_rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Per-ward, per-category growth series. Refuses aggregation. Never computes growth
    across a NULL value — such periods are flagged instead.
    Returns a list of output dicts (one per period in the filtered series).
    """
    if ward.strip().lower() in {"all", "*"}:
        _refuse("all-ward aggregation is not permitted. Specify a single ward.")
    if category.strip().lower() in {"all", "*"}:
        _refuse("all-category aggregation is not permitted. Specify one category.")

    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not series:
        _refuse(f"no rows for ward={ward!r} category={category!r}. "
                f"Check exact spelling (e.g. en-dash in ward names).")
    series.sort(key=lambda r: r["period"])

    # offset: MoM compares to the previous row (1 month); YoY would be 12 months.
    offset = 1 if growth_type == "MoM" else 12

    out = []
    for i, r in enumerate(series):
        cur_raw = (r.get("actual_spend") or "").strip()
        note = (r.get("notes") or "").strip()
        row = {
            "period": r["period"], "ward": ward, "category": category,
            "actual_spend": cur_raw if cur_raw else "NULL",
            "growth_percentage": "", "formula_applied": FORMULAS[growth_type],
            "null_flag_reason": "",
        }

        if not cur_raw:
            row["growth_percentage"] = "n/a"
            row["null_flag_reason"] = note or "actual_spend is NULL"
            out.append(row)
            continue

        prior_idx = i - offset
        if prior_idx < 0:
            row["growth_percentage"] = "n/a"
            row["null_flag_reason"] = f"no prior period ({growth_type}) to compare"
            out.append(row)
            continue

        prior = series[prior_idx]
        prior_raw = (prior.get("actual_spend") or "").strip()
        if not prior_raw:
            row["growth_percentage"] = "n/a"
            row["null_flag_reason"] = (
                f"prior period {prior['period']} actual_spend is NULL "
                f"({(prior.get('notes') or '').strip() or 'no reason'}) — "
                f"growth not computed")
            out.append(row)
            continue

        cur, prv = float(cur_raw), float(prior_raw)
        if prv == 0:
            row["growth_percentage"] = "n/a"
            row["null_flag_reason"] = "prior period is 0 — growth undefined"
        else:
            row["growth_percentage"] = f"{(cur - prv) / prv * 100:.1f}"
        out.append(row)

    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", dest="growth_type", default=None,
                        help="MoM or YoY — mandatory, never guessed")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.growth_type is None:
        _refuse("--growth-type not specified. Choose MoM or YoY; the tool will "
                "not guess the growth method.")
    if args.growth_type not in VALID_GROWTH:
        _refuse(f"--growth-type must be one of {sorted(VALID_GROWTH)}, "
                f"got {args.growth_type!r}.")

    rows, _ = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)

    computed = sum(1 for r in results if r["growth_percentage"] not in ("", "n/a"))
    print(f"Wrote {len(results)} rows to {args.output} "
          f"({computed} growth values computed, "
          f"{len(results) - computed} flagged).")


if __name__ == "__main__":
    main()
