"""
UC-0C — Number That Looks Right
Built with the RICE + agents.md + skills.md + CRAFT workflow.

Enforcement implemented here (mirrors agents.md):
- one ward + one category only; 'all'/missing scope -> REFUSE
- --growth-type missing -> REFUSE (never guess); YoY -> REFUSE (single-year data)
- all 5 null actual_spend rows reported at load time and flagged in output,
  never skipped, zero-filled, or interpolated
- formula shown on every output row
"""
import argparse
import csv
import sys

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
AGGREGATE_WORDS = {"all", "*", "all wards", "all categories", "every", "total"}


def _norm(value: str) -> str:
    """Normalise dashes/spaces so 'Ward 1 - Kasba' matches 'Ward 1 – Kasba'."""
    return " ".join(value.replace("–", "-").replace("—", "-").split()).lower()


def refuse(message: str):
    sys.exit("REFUSED: " + message)


def load_dataset(path: str):
    """Read CSV, validate columns, report every null actual_spend row, return rows."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [c for c in EXPECTED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                sys.exit("Input file %s is missing expected columns: %s" % (path, ", ".join(missing)))
            rows = list(reader)
    except OSError as exc:
        sys.exit("Cannot read input file %s: %s" % (path, exc))

    nulls = []
    for row in rows:
        raw = (row["actual_spend"] or "").strip()
        row["actual_spend"] = float(raw) if raw else None
        if row["actual_spend"] is None:
            nulls.append(row)

    print("NULL REPORT — %d row(s) with missing actual_spend (flagged, not computed):" % len(nulls))
    for row in nulls:
        print("  %s | %s | %s | reason: %s"
              % (row["period"], row["ward"], row["category"], row["notes"].strip() or "not stated"))
    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Per-period MoM growth for exactly one ward + one category, formula shown."""
    subset = sorted(
        (r for r in rows if _norm(r["ward"]) == _norm(ward) and _norm(r["category"]) == _norm(category)),
        key=lambda r: r["period"],
    )
    if not subset:
        wards = sorted({r["ward"] for r in rows})
        categories = sorted({r["category"] for r in rows})
        sys.exit("No rows for ward=%r category=%r.\nValid wards: %s\nValid categories: %s"
                 % (ward, category, "; ".join(wards), "; ".join(categories)))

    results = []
    prev_spend = None
    for i, row in enumerate(subset):
        spend = row["actual_spend"]
        result = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "actual_spend": "" if spend is None else spend,
            "formula": "",
            "growth_pct": "",
            "flag": "",
        }
        if spend is None:
            result["growth_pct"] = "NOT_COMPUTED"
            result["flag"] = "NULL_ACTUAL_SPEND: " + (row["notes"].strip() or "no reason recorded")
        elif i == 0:
            result["growth_pct"] = "N/A"
            result["flag"] = "FIRST_PERIOD_NO_BASELINE"
        elif prev_spend is None:
            result["growth_pct"] = "NOT_COMPUTED"
            result["flag"] = "PRIOR_PERIOD_NULL_NO_BASELINE"
        else:
            growth = (spend - prev_spend) / prev_spend * 100
            result["formula"] = "(%s-%s)/%s*100" % (spend, prev_spend, prev_spend)
            result["growth_pct"] = "%+.1f%%" % growth
        prev_spend = spend
        results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exactly one ward, e.g. 'Ward 1 - Kasba'")
    parser.add_argument("--category", help="Exactly one category, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", dest="growth_type", help="MoM (YoY impossible: single-year data)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Refusal conditions (agents.md rules 1 and 2) — refuse, never guess
    if not args.ward or _norm(args.ward) in AGGREGATE_WORDS:
        refuse("growth must be computed per ward. Pass --ward with exactly one ward name. "
               "Aggregating across all wards hides ward-level variation and null rows.")
    if not args.category or _norm(args.category) in AGGREGATE_WORDS:
        refuse("growth must be computed per category. Pass --category with exactly one category name.")
    if not args.growth_type:
        refuse("--growth-type not specified. State MoM explicitly — this system never guesses a formula.")
    if args.growth_type.lower() != "mom":
        refuse("growth type %r is not supported. Dataset covers 2024-01..2024-12 only, so YoY has no "
               "baseline year. Use --growth-type MoM." % args.growth_type)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend",
                                               "formula", "growth_pct", "flag"])
        writer.writeheader()
        writer.writerows(results)

    print("Wrote %d per-period rows for %s / %s (MoM) to %s"
          % (len(results), args.ward, args.category, args.output))


if __name__ == "__main__":
    main()
