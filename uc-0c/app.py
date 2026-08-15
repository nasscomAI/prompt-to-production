"""
UC-0C app.py — Ward Budget MoM Growth Analyzer
===============================================
Computes month-over-month growth for ONE ward + ONE category from the
ward budget CSV and writes a per-period table.

Enforcement (see agents.md):
- never aggregate across wards or categories — refuse instead
- flag every null actual_spend row before computing, citing the notes column
- show the formula used in every output row
- if --growth-type is missing or unsupported, refuse and ask, never guess
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH_TYPES = ["MoM"]
AGGREGATION_WORDS = {"all", "any", "every", "total", "combined", "*", ""}


def _normalise_ward_name(name: str) -> str:
    """Ward names use an en-dash in the data; be forgiving about the dash."""
    return name.replace("\u2013", "-").replace("\u2014", "-").strip()


def load_dataset(input_path: str) -> list:
    """
    Read the budget CSV, validate required columns, report null rows.
    Returns a list of row dicts with actual_spend parsed to float or None.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print("Error: input CSV has no header row.", file=sys.stderr)
                sys.exit(1)
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                print("Error: input CSV is missing required column(s): %s" % ", ".join(missing),
                      file=sys.stderr)
                sys.exit(1)
            rows = []
            for i, raw in enumerate(reader):
                row = dict(raw)
                row["_line"] = i + 2  # 1-based line including header
                raw_spend = (row.get("actual_spend") or "").strip()
                if raw_spend == "":
                    row["actual_spend"] = None
                else:
                    try:
                        row["actual_spend"] = float(raw_spend)
                    except ValueError:
                        row["actual_spend"] = None
                        row["_bad_spend"] = raw_spend
                try:
                    row["budgeted_amount"] = float((row.get("budgeted_amount") or "").strip())
                except ValueError:
                    row["budgeted_amount"] = None
                rows.append(row)
    except FileNotFoundError:
        print("Error: input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print("Error: cannot read input file %s: %s" % (input_path, exc), file=sys.stderr)
        sys.exit(1)

    null_rows = [r for r in rows if r["actual_spend"] is None]
    print("Loaded %d rows from %s. %d row(s) have a NULL actual_spend:" % (len(rows), input_path, len(null_rows)))
    for r in null_rows:
        print("  - %s | %s | %s | reason: %s"
              % (r["period"], r["ward"], r["category"], (r.get("notes") or "").strip() or "no note given"))
    return rows


def _refuse(message: str):
    print("REFUSED: %s" % message, file=sys.stderr)
    sys.exit(1)


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for one ward + one category.
    Returns output rows with formula and flags. Refuses aggregation.
    """
    ward_lookup = {_normalise_ward_name(w): w for w in sorted({r["ward"] for r in rows})}
    category_lookup = sorted({r["category"] for r in rows})

    if growth_type not in SUPPORTED_GROWTH_TYPES:
        _refuse("growth type '%s' is not supported. Supported: %s. "
                "Never guess a formula — specify the growth type explicitly."
                % (growth_type, ", ".join(SUPPORTED_GROWTH_TYPES)))

    if ward.lower() in AGGREGATION_WORDS or category.lower() in AGGREGATION_WORDS:
        _refuse("aggregation across wards or categories is not permitted. "
                "Provide exactly one ward and one category.")

    target_ward = ward_lookup.get(_normalise_ward_name(ward))
    if target_ward is None:
        _refuse("ward '%s' not found in dataset. Valid wards: %s"
                % (ward, ", ".join(sorted(ward_lookup.values()))))

    if category not in category_lookup:
        _refuse("category '%s' not found in dataset. Valid categories: %s"
                % (category, ", ".join(category_lookup)))

    filtered = [r for r in rows if r["ward"] == target_ward and r["category"] == category]
    if not filtered:
        _refuse("no data rows found for ward '%s' + category '%s'." % (target_ward, category))

    filtered.sort(key=lambda r: r["period"])
    output = []
    prev = None
    prev_period = None
    for r in filtered:
        period = r["period"]
        spend = r["actual_spend"]
        notes = (r.get("notes") or "").strip()
        if spend is None:
            output.append({
                "period": period,
                "ward": target_ward,
                "category": category,
                "budgeted_amount": r["budgeted_amount"],
                "actual_spend": "NULL",
                "prev_period": prev_period or "",
                "prev_actual_spend": "" if prev is None else prev,
                "growth_pct": "N/A",
                "formula": "n/a",
                "flag": "NULL_SPEND",
                "notes": notes or "no note given",
            })
        elif prev is None:
            output.append({
                "period": period,
                "ward": target_ward,
                "category": category,
                "budgeted_amount": r["budgeted_amount"],
                "actual_spend": spend,
                "prev_period": prev_period or "",
                "prev_actual_spend": "",
                "growth_pct": "N/A",
                "formula": "n/a (no previous period to compare)",
                "flag": "NO_PREV_PERIOD",
                "notes": notes,
            })
        else:
            growth = (spend - prev) / prev * 100.0
            output.append({
                "period": period,
                "ward": target_ward,
                "category": category,
                "budgeted_amount": r["budgeted_amount"],
                "actual_spend": spend,
                "prev_period": prev_period,
                "prev_actual_spend": prev,
                "growth_pct": "%.1f%%" % growth,
                "formula": "((%s - %s) / %s) * 100" % (spend, prev, prev),
                "flag": "",
                "notes": notes,
            })
        prev = spend
        prev_period = period
    return output


def write_output(rows: list, output_path: str):
    fields = ["period", "ward", "category", "budgeted_amount", "actual_spend",
              "prev_period", "prev_actual_spend", "growth_pct", "formula", "flag", "notes"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote %d period rows to %s" % (len(rows), output_path))


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget MoM Growth Analyzer")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name (refuse aggregation)")
    parser.add_argument("--category", required=True, help="Single category name (refuse aggregation)")
    parser.add_argument("--growth-type", required=True,
                        help="Growth formula to apply. Supported: %s" % ", ".join(SUPPORTED_GROWTH_TYPES))
    parser.add_argument("--output", required=True, help="Path to write growth table CSV")
    args = parser.parse_args()

    rows = load_dataset(args.input)
    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(growth_rows, args.output)


if __name__ == "__main__":
    main()