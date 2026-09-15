"""
UC-0C - Number That Looks Right

Implements the enforcement rules declared in uc-0c/agents.md:

  NO AGGREGATION            one (ward, category) series at a time; ALL means iterate, never combine
  NULLS REPORTED FIRST      missing actual_spend is listed with its source reason before any arithmetic
  MISSING BASE PROPAGATES   a null at period N leaves period N+1 uncomputable; gaps are never bridged
  SHOW THE FORMULA          every row carries its calculation with the numbers substituted
  REFUSE, DO NOT GUESS      unstated or impossible growth-type, unknown ward/category -> refuse, exit non-zero

Standard library only. Deterministic.

Usage:
    python app.py --input ../data/budget/ward_budget.csv \
                  --ward "Ward 1 - Kasba" \
                  --category "Roads & Pothole Repair" \
                  --growth-type MoM \
                  --output growth_output.csv
"""

import argparse
import csv
import re
import sys
from typing import Dict, List, Optional

REQUIRED_COLUMNS = ["period", "ward", "category", "actual_spend", "notes"]

OUTPUT_COLUMNS = [
    "ward", "category", "period", "actual_spend", "prior_period", "prior_spend",
    "growth_type", "growth_pct", "formula", "status", "note",
]

GROWTH_TYPES = {
    "MoM": "month over month - each period against the period immediately before it",
    "YoY": "year over year - each period against the same month of the previous year",
}

# Values that would mean an aggregated row had reached the output file.
FORBIDDEN_LABELS = {"", "all", "total", "aggregate", "combined", "sum"}


def _normalise(value: str) -> str:
    """Fold case, whitespace, and en dash vs hyphen - and nothing else.

    This exists so a hyphen typed at the command line matches the en dash in the
    source data. It is deliberately not fuzzy matching: a near-miss ward name
    silently analysing the wrong ward is worse than a failed run.
    """
    value = (value or "").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", value).strip().lower()


# --------------------------------------------------------------------------
# Skill: load_dataset
# --------------------------------------------------------------------------

def load_dataset(path: str) -> dict:
    """Read the budget CSV, validate the schema, and report nulls before any maths."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            raw_rows = list(csv.DictReader(handle))
    except FileNotFoundError:
        sys.stderr.write("ERROR: input file not found: {}\n".format(path))
        sys.exit(1)
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write("ERROR: could not read {}: {}\n".format(path, exc))
        sys.exit(1)

    if not raw_rows:
        sys.stderr.write("ERROR: {} contains no data rows.\n".format(path))
        sys.exit(1)

    found = list(raw_rows[0].keys())
    missing = [c for c in REQUIRED_COLUMNS if c not in found]
    if missing:
        sys.stderr.write(
            "ERROR: {} is missing required column(s): {}. Columns found: {}\n"
            .format(path, ", ".join(missing), ", ".join(found)))
        sys.exit(1)

    rows: List[dict] = []
    nulls: List[dict] = []

    for raw in raw_rows:
        spend_text = (raw.get("actual_spend") or "").strip()
        notes = (raw.get("notes") or "").strip()
        spend: Optional[float] = None
        reason = ""

        if not spend_text:
            reason = notes or "no reason given in source"
        else:
            try:
                spend = float(spend_text)
            except ValueError:
                # Never coerce to 0, never drop the row - record why it failed.
                reason = "actual_spend {!r} is not numeric".format(spend_text)

        row = {
            "period": (raw.get("period") or "").strip(),
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "actual_spend": spend,
            "notes": notes,
            "null_reason": reason,
        }
        rows.append(row)
        if spend is None:
            nulls.append(row)

    periods = sorted({r["period"] for r in rows if r["period"]})
    years = sorted({p.split("-")[0] for p in periods if "-" in p})

    # NULLS REPORTED FIRST - printed before any arithmetic is allowed to run.
    sys.stderr.write("Null report for {}\n".format(path))
    sys.stderr.write("  rows read:                {}\n".format(len(rows)))
    sys.stderr.write("  rows missing actual_spend: {}\n".format(len(nulls)))
    for row in nulls:
        sys.stderr.write("    {} | {} | {} | reason: {}\n".format(
            row["period"], row["ward"], row["category"], row["null_reason"]))
    sys.stderr.write("  periods: {} ({} to {})  years present: {}\n\n".format(
        len(periods), periods[0] if periods else "-",
        periods[-1] if periods else "-", ", ".join(years)))

    return {
        "rows": rows,
        "wards": sorted({r["ward"] for r in rows if r["ward"]}),
        "categories": sorted({r["category"] for r in rows if r["category"]}),
        "periods": periods,
        "years": years,
        "nulls": nulls,
    }


# --------------------------------------------------------------------------
# Skill: resolve_selector
# --------------------------------------------------------------------------

def resolve_selector(selector: str, available: List[str], label: str) -> List[str]:
    """Resolve a --ward/--category argument to exact dataset values, or refuse.

    ALL means iterate over each value separately. It never means combine them.
    """
    if selector is None or not selector.strip():
        sys.stderr.write(
            "REFUSED: --{} was not supplied.\n"
            "  This tool reports one {} at a time. Omitting it would mean aggregating\n"
            "  across every {}, which produces a number no ward office can act on.\n"
            "  Supply an exact value, or ALL to emit each one as its own labelled series.\n"
            "  Available: {}\n".format(label, label, label, "; ".join(available)))
        sys.exit(2)

    if _normalise(selector) == "all":
        return list(available)

    for value in available:
        if _normalise(value) == _normalise(selector):
            return [value]

    sys.stderr.write(
        "REFUSED: {} {!r} is not present in the dataset.\n"
        "  Not resolved to the closest match - analysing the wrong {} silently is\n"
        "  worse than failing. Available values:\n".format(label, selector, label))
    for value in available:
        sys.stderr.write("    {}\n".format(value))
    sys.exit(2)


# --------------------------------------------------------------------------
# Skill: compute_growth
# --------------------------------------------------------------------------

def _prior_period(period: str, growth_type: str) -> str:
    year, month = period.split("-")
    if growth_type == "YoY":
        return "{:04d}-{}".format(int(year) - 1, month)
    month_num = int(month)
    if month_num == 1:
        return "{:04d}-12".format(int(year) - 1)
    return "{}-{:02d}".format(year, month_num - 1)


def compute_growth(rows: List[dict], growth_type: str,
                   ward: str, category: str) -> List[dict]:
    """Compute per-period growth for one ward and one category.

    Every period appears exactly once, computed or not. Gaps are never bridged.
    """
    series = sorted([r for r in rows
                     if r["ward"] == ward and r["category"] == category],
                    key=lambda r: r["period"])
    by_period: Dict[str, dict] = {r["period"]: r for r in series}

    results: List[dict] = []
    for row in series:
        period = row["period"]
        prior_key = _prior_period(period, growth_type)
        prior_row = by_period.get(prior_key)

        current = row["actual_spend"]
        prior = prior_row["actual_spend"] if prior_row else None

        record = {
            "ward": ward,
            "category": category,
            "period": period,
            "actual_spend": "" if current is None else "{:g}".format(current),
            "prior_period": prior_key if prior_row else "",
            "prior_spend": "" if prior is None else "{:g}".format(prior),
            "growth_type": growth_type,
            "growth_pct": "",
            "formula": "",
            "status": "",
            "note": "",
        }

        if current is None:
            record["status"] = "NULL_INPUT"
            record["formula"] = "not computed - actual_spend is missing for this period"
            record["note"] = row["null_reason"]

        elif prior_row is None:
            record["status"] = "NO_PRIOR_PERIOD"
            record["formula"] = (
                "not computed - {} has no prior period in this dataset".format(period))
            record["note"] = "first period of the series under {}".format(growth_type)

        elif prior is None:
            # A null at N leaves N+1 uncomputable. Reaching further back to close
            # the gap would silently measure two periods and look correct.
            record["status"] = "NULL_PRIOR"
            record["formula"] = (
                "not computed - base period {} has no actual_spend".format(prior_key))
            record["note"] = "base missing: {}".format(prior_row["null_reason"])

        elif prior == 0:
            record["status"] = "ZERO_BASE"
            record["formula"] = (
                "not computed - base period {} is 0; growth from zero is undefined"
                .format(prior_key))
            record["note"] = "undefined, not infinite and not 100%"

        else:
            growth = (current - prior) / prior * 100.0
            record["growth_pct"] = "{:+.1f}".format(growth)
            record["formula"] = "({:g} - {:g}) / {:g} * 100 = {:+.1f}%".format(
                current, prior, prior, growth)
            record["status"] = "OK"

        results.append(record)

    return results


# --------------------------------------------------------------------------
# Skill: write_growth_table
# --------------------------------------------------------------------------

def write_growth_table(rows: List[dict], output_path: str) -> int:
    """Validate the contract, then write growth_output.csv."""
    for row in rows:
        # Last gate against an aggregated row reaching the file.
        if _normalise(row["ward"]) in FORBIDDEN_LABELS:
            sys.stderr.write("ERROR: aggregated ward label {!r} in output. Refusing to "
                             "write.\n".format(row["ward"]))
            sys.exit(1)
        if _normalise(row["category"]) in FORBIDDEN_LABELS:
            sys.stderr.write("ERROR: aggregated category label {!r} in output. Refusing "
                             "to write.\n".format(row["category"]))
            sys.exit(1)
        if row["growth_pct"] and row["status"] != "OK":
            sys.stderr.write("ERROR: row {} {} has a growth figure with status {}. "
                             "Refusing to write.\n".format(
                                 row["ward"], row["period"], row["status"]))
            sys.exit(1)
        if not row["formula"]:
            sys.stderr.write("ERROR: row {} {} has no formula. Refusing to write.\n"
                             .format(row["ward"], row["period"]))
            sys.exit(1)

    try:
        with open(output_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        sys.stderr.write("ERROR: could not write {}: {}\n".format(output_path, exc))
        sys.exit(1)

    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    sys.stderr.write("Summary\n")
    sys.stderr.write("  rows written: {}\n".format(len(rows)))
    for status in ("OK", "NULL_INPUT", "NULL_PRIOR", "NO_PRIOR_PERIOD", "ZERO_BASE"):
        if status in counts:
            sys.stderr.write("  {:<16} {}\n".format(status + ":", counts[status]))
    series_count = len({(r["ward"], r["category"]) for r in rows})
    sys.stderr.write("  distinct ward/category series: {} (never combined)\n"
                     .format(series_count))
    return len(rows)


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator",
        epilog="--growth-type is intentionally not defaulted. See agents.md.")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help='Exact ward name, or ALL to emit each separately')
    parser.add_argument("--category", help='Exact category name, or ALL')
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY - required, never inferred")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    data = load_dataset(args.input)

    # REFUSE, DO NOT GUESS - method must be stated.
    if not args.growth_type:
        sys.stderr.write("REFUSED: --growth-type was not supplied.\n")
        sys.stderr.write("  Choosing for you would hide which comparison produced the "
                         "numbers. Options:\n")
        for name, meaning in GROWTH_TYPES.items():
            sys.stderr.write("    {:<5} {}\n".format(name, meaning))
        sys.exit(2)

    growth_type = args.growth_type.strip()
    match = [k for k in GROWTH_TYPES if k.lower() == growth_type.lower()]
    if not match:
        sys.stderr.write("REFUSED: unknown --growth-type {!r}. Valid: {}\n".format(
            args.growth_type, ", ".join(GROWTH_TYPES)))
        sys.exit(2)
    growth_type = match[0]

    # REFUSE, DO NOT GUESS - method must be possible against this data.
    if growth_type == "YoY" and len(data["years"]) < 2:
        sys.stderr.write(
            "REFUSED: YoY needs at least two years of data; this dataset contains "
            "only {}.\n"
            "  Every comparison would have no prior-year period. Emitting twelve blank\n"
            "  rows would imply the analysis was attempted. Use --growth-type MoM, or\n"
            "  supply a dataset spanning more than one year.\n".format(
                ", ".join(data["years"])))
        sys.exit(2)

    wards = resolve_selector(args.ward, data["wards"], "ward")
    categories = resolve_selector(args.category, data["categories"], "category")

    # NO AGGREGATION - iterate, label, never combine.
    all_rows: List[dict] = []
    for ward in wards:
        for category in categories:
            all_rows.extend(compute_growth(data["rows"], growth_type, ward, category))

    if not all_rows:
        sys.stderr.write("ERROR: no rows matched the requested ward and category.\n")
        sys.exit(1)

    write_growth_table(all_rows, args.output)
    print("Done. Growth table written to {}".format(args.output))


if __name__ == "__main__":
    main()