"""
UC-0C — Number That Looks Right

Vibe-coded with a RICE prompt and refined through the CRAFT loop. The
enforcement rules in agents.md are implemented directly here:

- never aggregate across wards or categories — refuse if asked
- flag every null row before computing and report the notes reason
- show the formula used in every output row alongside the result
- if --growth-type is not specified — refuse and ask, never guess
"""
import argparse
import csv
import os
import sys


def resolve_path(path):
    if os.path.exists(path):
        return path
    alt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "budget", os.path.basename(path))
    if os.path.exists(alt):
        return alt
    return path


def normalize_key(value):
    return (value or "").strip().replace("–", "-").replace("—", "-").lower()


def load_dataset(path):
    """Reads the CSV, validates columns, and reports every null row with its reason."""
    try:
        with open(path, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)
    except FileNotFoundError:
        print("Error: budget file not found: %s" % path)
        sys.exit(1)

    required = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
    missing = [c for c in required if c not in fieldnames]
    if missing:
        print("Error: budget file missing columns: %s" % ", ".join(missing))
        sys.exit(1)

    null_rows = [r for r in rows if not (r.get("actual_spend") or "").strip()]
    print("Loaded %d rows. Null actual_spend rows found: %d" % (len(rows), len(null_rows)))
    for r in null_rows:
        reason = (r.get("notes") or "").strip() or "no reason recorded"
        print("  NULL: %s | %s | %s | reason: %s" % (r["period"], r["ward"], r["category"], reason))

    return rows


def compute_growth(rows, ward, category, growth_type):
    """Per-ward per-category MoM growth table with formula and null flags."""
    if growth_type == "YoY":
        print("Refusing: YoY requires prior-year data, which is not present in ward_budget.csv. Please specify --growth-type MoM.")
        sys.exit(1)

    target_ward = normalize_key(ward)
    target_cat = normalize_key(category)

    slice_rows = [r for r in rows
                  if normalize_key(r["ward"]) == target_ward
                  and normalize_key(r["category"]) == target_cat]
    if not slice_rows:
        print("Refusing: no rows found for ward='%s' category='%s'." % (ward, category))
        sys.exit(1)

    slice_rows.sort(key=lambda r: r["period"])

    output = []
    prev = None
    for r in slice_rows:
        actual_raw = (r.get("actual_spend") or "").strip()
        row = {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": actual_raw if actual_raw else "NULL",
            "previous_actual_spend": prev if prev is not None else "n/a",
            "growth_percent": "",
            "formula": "",
            "flag": "",
        }
        if not actual_raw:
            note = (r.get("notes") or "").strip() or "no reason recorded"
            row["growth_percent"] = "NA"
            row["formula"] = "not computed (actual_spend is NULL)"
            row["flag"] = "NULL_FLAG: %s" % note
        elif prev is None:
            row["growth_percent"] = "n/a"
            row["formula"] = "first period in series — no previous actual_spend to compare"
        else:
            pv = float(prev)
            cv = float(actual_raw)
            growth = (cv - pv) / pv * 100.0
            row["growth_percent"] = "%+.1f%%" % growth
            row["formula"] = "MoM growth = ((%s - %s) / %s) * 100 = %+.1f%%" % (actual_raw, prev, prev, growth)
        output.append(row)
        if actual_raw:
            prev = actual_raw

    return output


def write_output(rows, path):
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                  "previous_actual_spend", "growth_percent", "formula", "flag"]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward (all-ward aggregation is refused)")
    parser.add_argument("--category", required=True, help="Single category")
    parser.add_argument("--growth-type", default=None, help="MoM (YoY refused: no prior-year data)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("Refusing: --growth-type not specified. Please specify MoM or YoY — I will not guess.")
        sys.exit(1)

    if normalize_key(args.ward) in ("all", "all wards", "all-wards"):
        print("Refusing: all-ward aggregation is not allowed. Specify a single ward.")
        sys.exit(1)

    if normalize_key(args.category) in ("all", "all categories", "all-categories"):
        print("Refusing: all-category aggregation is not allowed. Specify a single category.")
        sys.exit(1)

    # Never crash on non-ASCII output regardless of console encoding
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    path = resolve_path(args.input)
    rows = load_dataset(path)
    output = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(output, args.output)
    print("Wrote %d row(s) to %s (per-ward per-category table, growth type %s)." % (
        len(output), args.output, args.growth_type))


if __name__ == "__main__":
    main()
