"""
UC-0C — Number That Looks Right.
Per-ward per-category MoM growth calculator. Implements skills.md
(load_dataset, compute_growth) under agents.md enforcement.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_COLUMNS = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "flag"]
SUPPORTED_GROWTH_TYPES = ("MoM",)


def load_dataset(input_path):
    """Read CSV, validate schema, report null actual_spend rows. See skills.md."""
    try:
        f = open(input_path, "r", encoding="utf-8-sig", newline="")
    except FileNotFoundError:
        raise FileNotFoundError("Input file not found: " + str(input_path))
    with f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError("Missing required columns: %r. Found: %r" % (missing, reader.fieldnames))
        rows = list(reader)
    null_rows = [
        {"period": r["period"], "ward": r["ward"], "category": r["category"], "notes": r.get("notes", "")}
        for r in rows
        if (r.get("actual_spend") or "").strip() == ""
    ]
    print("Loaded %d rows. Null actual_spend count: %d" % (len(rows), len(null_rows)), file=sys.stderr)
    for n in null_rows:
        print("NULL: %s | %s | %s | %s" % (n["period"], n["ward"], n["category"], n["notes"]), file=sys.stderr)
    return {"rows": rows, "columns": reader.fieldnames, "null_count": len(null_rows), "null_rows": null_rows}


def _parse_spend(raw):
    s = (raw or "").strip()
    if s == "":
        return None
    return float(s)


def _fmt_growth(value):
    rounded = round(value, 1)
    if rounded == 0:
        rounded = 0.0
    sign = "+" if rounded >= 0 else "-"
    return "%s%.1f%%" % (sign, abs(rounded))


def compute_growth(dataset, ward, category, growth_type):
    """Return 12-row per-period table for one ward+category slice. See skills.md."""
    if not growth_type or growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            "REFUSED: --growth-type is required and must be one of %r. Got %r. "
            "Please re-run with an explicit --growth-type MoM." % (list(SUPPORTED_GROWTH_TYPES), growth_type)
        )
    valid_wards = sorted({r["ward"] for r in dataset["rows"]})
    valid_cats = sorted({r["category"] for r in dataset["rows"]})
    if ward not in valid_wards:
        raise ValueError("REFUSED: --ward %r does not match any dataset value. Valid wards: %r" % (ward, valid_wards))
    if category not in valid_cats:
        raise ValueError("REFUSED: --category %r does not match any dataset value. Valid categories: %r" % (category, valid_cats))
    low_ward, low_cat = (ward or "").strip().lower(), (category or "").strip().lower()
    if low_ward in ("all", "all wards", "*", "total") or low_cat in ("all", "all categories", "*", "total"):
        raise ValueError(
            "REFUSED: aggregation across wards/categories into a single number is not allowed. "
            "Request one ward + one category at a time for a per-period table."
        )
    sl = [r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category]
    sl.sort(key=lambda r: r["period"])
    if not sl:
        raise ValueError("REFUSED: no rows found for ward=%r category=%r." % (ward, category))

    out = []
    prev_val = None
    prev_raw = None
    for i, r in enumerate(sl):
        curr_raw = (r.get("actual_spend") or "").strip()
        curr_val = _parse_spend(r.get("actual_spend"))
        notes = (r.get("notes") or "").strip()
        if i == 0:
            if curr_val is None:
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": "", "growth_pct": "", "formula": "",
                            "flag": ("NULL \u2014 " + notes) if notes else "NULL \u2014 null actual_spend"})
            else:
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": curr_raw, "growth_pct": "", "formula": "",
                            "flag": "BASE \u2014 no prior period"})
        else:
            if curr_val is None:
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": "", "growth_pct": "", "formula": "",
                            "flag": ("NULL \u2014 " + notes) if notes else "NULL \u2014 null actual_spend"})
            elif prev_val is None:
                prev_notes = (sl[i - 1].get("notes") or "").strip()
                reason = prev_notes if prev_notes else "null prior actual_spend"
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": curr_raw, "growth_pct": "", "formula": "",
                            "flag": "NULL \u2014 prior period not computable (%s)" % reason})
            elif prev_val == 0:
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": curr_raw, "growth_pct": "", "formula": "",
                            "flag": "UNDEFINED \u2014 prior spend is zero"})
            else:
                g = (curr_val - prev_val) / prev_val * 100
                g_str = _fmt_growth(g)
                formula = "(%s - %s) / %s x 100 = %s" % (curr_raw, prev_raw, prev_raw, g_str)
                out.append({"period": r["period"], "ward": ward, "category": category,
                            "actual_spend": curr_raw, "growth_pct": g_str, "formula": formula, "flag": ""})
        prev_val = curr_val
        prev_raw = curr_raw if curr_val is not None else None
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-0C per-ward per-category MoM growth calculator.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", default=None, dest="growth_type")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    try:
        dataset = load_dataset(args.input)
        table = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except (FileNotFoundError, ValueError) as e:
        print("Error: %s" % e, file=sys.stderr)
        return 2

    parent = os.path.dirname(os.path.abspath(args.output))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(table)
    print("Wrote %d rows to %s" % (len(table), args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
