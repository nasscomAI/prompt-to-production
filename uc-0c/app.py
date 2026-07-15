"""
UC-0C — Number That Looks Right

Deterministic budget-growth calculator. It enforces the RICE rules from README.md:
  - never aggregate across wards or categories — refuse if asked
  - flag every null actual_spend row before computing (report the note reason)
  - show the formula used in every output row
  - if --growth-type is not specified, refuse and ask — never guess

Run:
  python app.py --input ../data/budget/ward_budget.csv \
                --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
                --growth-type MoM --output growth_output.csv
"""
import argparse
import csv
import sys

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
AGGREGATE_TOKENS = {"", "all", "any", "*", "everything", "total"}


class RefusalError(Exception):
    """Raised when the request violates an enforcement rule and must be refused."""


def load_dataset(path: str):
    """
    Read the budget CSV, validate columns, and report null actual_spend rows
    before returning.

    Returns (rows, null_rows) where rows is a list of dicts and null_rows is the
    subset whose actual_spend is blank.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in EXPECTED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise RefusalError("Input is missing required columns: %s" % ", ".join(missing))
        rows = list(reader)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]

    print("Loaded %d rows. Found %d null actual_spend row(s):" % (len(rows), len(null_rows)))
    for r in null_rows:
        print("  - %s · %s · %s → %s"
              % (r["period"], r["ward"], r["category"],
                 (r.get("notes") or "(no reason given)").strip()))
    print("")
    return rows, null_rows


def _is_aggregate_request(value: str) -> bool:
    return (value or "").strip().lower() in AGGREGATE_TOKENS


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """
    Compute per-period growth for a SINGLE ward + category.

    Enforcement:
      - refuse if ward or category is an aggregate ('all', 'any', blank, ...)
      - refuse if growth_type is not MoM or YoY
      - null periods are flagged, not computed
      - every computed row carries the formula string
    """
    if _is_aggregate_request(ward) or _is_aggregate_request(category):
        raise RefusalError(
            "REFUSED: cross-ward / cross-category aggregation is not permitted. "
            "Specify one exact --ward and one exact --category.")

    gt = (growth_type or "").strip()
    if gt not in ("MoM", "YoY"):
        raise RefusalError(
            "REFUSED: --growth-type must be explicitly 'MoM' or 'YoY'. "
            "I will not guess which one you meant.")

    # Filter to the one ward+category, ordered by period.
    subset = [r for r in rows
              if r["ward"].strip() == ward.strip()
              and r["category"].strip() == category.strip()]
    subset.sort(key=lambda r: r["period"])
    if not subset:
        raise RefusalError(
            "No rows for ward=%r category=%r. Check exact spelling (including the – dash)."
            % (ward, category))

    # Map period → actual_spend (float or None) for prior-period lookups.
    def spend(r):
        v = (r.get("actual_spend") or "").strip()
        return float(v) if v else None

    by_period = {r["period"]: r for r in subset}
    offset = 1 if gt == "MoM" else 12  # months back for the comparison period

    def prior_period(period):
        y, m = period.split("-")
        idx = (int(y) * 12 + (int(m) - 1)) - offset
        return "%04d-%02d" % (idx // 12, idx % 12 + 1)

    out_rows = []
    for r in subset:
        period = r["period"]
        cur = spend(r)
        prev_key = prior_period(period)
        prev_row = by_period.get(prev_key)
        prev = spend(prev_row) if prev_row else None

        row = {
            "period": period,
            "ward": ward.strip(),
            "category": category.strip(),
            "budgeted_amount": r.get("budgeted_amount", ""),
            "actual_spend": "" if cur is None else cur,
            "growth_type": gt,
            "growth_pct": "",
            "formula": "",
            "flag": "",
        }

        if cur is None:
            row["flag"] = "NULL — not computed: %s" % (r.get("notes") or "no reason given").strip()
        elif prev_row is None:
            row["flag"] = "no comparison period (%s absent)" % prev_key
        elif prev is None:
            row["flag"] = "prior period %s is NULL — not computed: %s" % (
                prev_key, (prev_row.get("notes") or "no reason given").strip())
        elif prev == 0:
            row["flag"] = "prior period %s is 0 — growth undefined" % prev_key
        else:
            pct = (cur - prev) / prev * 100.0
            row["growth_pct"] = "%+.1f%%" % pct
            row["formula"] = "%s = (%.1f - %.1f) / %.1f * 100 = %+.1f%%" % (
                gt, cur, prev, prev, pct)

        out_rows.append(row)

    return out_rows


def write_output(out_rows, output_path):
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "growth_type", "growth_pct", "formula", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", default="", help="Exact ward name (no aggregation)")
    parser.add_argument("--category", default="", help="Exact category name (no aggregation)")
    parser.add_argument("--growth-type", dest="growth_type", default="",
                        help="MoM or YoY — required, never guessed")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    rows, _null = load_dataset(args.input)
    try:
        out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    except RefusalError as exc:
        print(str(exc))
        sys.exit(2)

    write_output(out_rows, args.output)
    computed = sum(1 for r in out_rows if r["growth_pct"])
    print("Wrote %d period rows (%d computed, %d flagged) to %s"
          % (len(out_rows), computed, len(out_rows) - computed, args.output))


if __name__ == "__main__":
    main()
