"""
UC-0C — Budget Growth Calculator

Implements the contract in agents.md / skills.md.

Two design choices carry the enforcement:
  1. A blank actual_spend parses to None, never 0.0 — zero is a real spend
     figure and must never be confused with "not reported".
  2. The MoM base is resolved by calendar arithmetic, not by taking the previous
     row in the file. A missing month must surface as NO_PRIOR_PERIOD rather than
     silently borrowing an older month as the denominator.
"""
import argparse
import csv
import os
import sys

REQUIRED_COLUMNS = ["period", "ward", "category",
                    "budgeted_amount", "actual_spend", "notes"]

OUTPUT_FIELDS = ["ward", "category", "period", "budgeted_amount", "actual_spend",
                 "growth_type", "base_period", "base_value", "formula",
                 "growth_pct", "status", "note"]

VALID_GROWTH_TYPES = ["MoM", "YoY"]

AGGREGATE_TOKENS = {"all", "all wards", "all categories", "*",
                    "any", "total", "combined", "everything"}


class AggregationRefused(Exception):
    pass


class GrowthTypeNotSpecified(Exception):
    pass


class EmptySelection(Exception):
    pass


def _normalise_name(value):
    """Match across dash variants; the source spelling is what gets emitted."""
    return (value or "").replace("–", "-").replace("—", "-") \
                        .replace("  ", " ").strip().lower()


def _parse_amount(raw):
    text = (raw or "").strip()
    if not text:
        return None, ""
    try:
        return float(text), ""
    except ValueError:
        return None, text


def _shift_period(period, months):
    year, month = int(period[:4]), int(period[5:7])
    index = year * 12 + (month - 1) + months
    return "{:04d}-{:02d}".format(index // 12, index % 12 + 1)


def load_dataset(path: str) -> dict:
    """Read the budget CSV, validate columns, report nulls before returning."""
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("missing required column(s): {}".format(", ".join(missing)))
        raw_rows = list(reader)

    rows, nulls, seen = [], [], {}
    for raw in raw_rows:
        actual, bad_text = _parse_amount(raw.get("actual_spend"))
        budgeted, _ = _parse_amount(raw.get("budgeted_amount"))
        row = {
            "period": (raw.get("period") or "").strip(),
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "budgeted_amount": budgeted,
            "actual_spend": actual,
            "notes": (raw.get("notes") or "").strip(),
        }
        rows.append(row)

        key = (row["ward"], row["category"], row["period"])
        seen[key] = seen.get(key, 0) + 1

        if actual is None:
            nulls.append({
                "period": row["period"], "ward": row["ward"],
                "category": row["category"],
                "note": row["notes"] or "(no reason given in source)",
                "raw_value": bad_text,
            })

    duplicates = [k for k, count in seen.items() if count > 1]

    print("loaded {} rows from {}".format(len(rows), os.path.basename(path)))
    print("NULL actual_spend rows: {} — flagged before any computation".format(len(nulls)))
    for null in nulls:
        print("  - {} | {} | {} | reason: {}".format(
            null["period"], null["ward"], null["category"], null["note"]))
    if duplicates:
        print("WARNING: duplicate ward+category+period keys: {}".format(duplicates))
    print("")

    return {
        "rows": rows,
        "nulls": nulls,
        "duplicates": duplicates,
        "wards": sorted({r["ward"] for r in rows}),
        "categories": sorted({r["category"] for r in rows}),
        "periods": sorted({r["period"] for r in rows}),
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str):
    """One ward, one category. Refuses anything that would aggregate or guess."""
    if not growth_type:
        raise GrowthTypeNotSpecified(
            "--growth-type not specified. This changes every number in the output, "
            "so it will not be guessed. Choose one of: {}".format(
                ", ".join(VALID_GROWTH_TYPES)))
    if growth_type not in VALID_GROWTH_TYPES:
        raise GrowthTypeNotSpecified(
            "unknown growth type '{}'. Valid: {}".format(
                growth_type, ", ".join(VALID_GROWTH_TYPES)))

    for label, value in (("--ward", ward), ("--category", category)):
        if not value or _normalise_name(value) in AGGREGATE_TOKENS:
            raise AggregationRefused(
                "REFUSED: {} was '{}'. Growth is only meaningful per ward per "
                "category — wards differ in budget and population, so a combined "
                "figure is not a real quantity. Name one ward and one category."
                .format(label, value or "(omitted)"))

    ward_key, category_key = _normalise_name(ward), _normalise_name(category)
    selected = [r for r in dataset["rows"]
                if _normalise_name(r["ward"]) == ward_key
                and _normalise_name(r["category"]) == category_key]

    if not selected:
        raise EmptySelection(
            "REFUSED: no rows match ward='{}' category='{}'. Writing an empty "
            "table would be indistinguishable from a real result.\n"
            "  valid wards     : {}\n  valid categories: {}".format(
                ward, category, dataset["wards"], dataset["categories"]))

    by_period = {r["period"]: r for r in selected}
    offset = -1 if growth_type == "MoM" else -12
    results = []

    for period in sorted(by_period):
        row = by_period[period]
        base_period = _shift_period(period, offset)
        base_row = by_period.get(base_period)

        entry = {
            "ward": row["ward"],
            "category": row["category"],
            "period": period,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": "" if row["actual_spend"] is None else row["actual_spend"],
            "growth_type": growth_type,
            "base_period": base_period,
            "base_value": "",
            "formula": "",
            "growth_pct": "",
            "status": "",
            "note": "",
        }

        if row["actual_spend"] is None:
            entry["status"] = "NULL_VALUE"
            entry["note"] = row["notes"] or "(no reason given in source)"
            entry["formula"] = "not computed — actual_spend is null"
        elif base_row is None:
            entry["status"] = "NO_PRIOR_PERIOD"
            entry["base_period"] = ""
            entry["note"] = ("no data for {} ({} baseline)".format(base_period, growth_type)
                             if growth_type == "MoM"
                             else "dataset covers 2024 only, so no prior-year baseline exists")
            if growth_type == "YoY":
                entry["status"] = "NOT_COMPUTABLE"
            entry["formula"] = "not computed — no baseline period"
        elif base_row["actual_spend"] is None:
            entry["status"] = "NULL_BASE"
            entry["base_value"] = ""
            entry["note"] = "baseline {} is null: {}".format(
                base_period, base_row["notes"] or "(no reason given in source)")
            entry["formula"] = "not computed — baseline value is null"
        elif base_row["actual_spend"] == 0:
            entry["status"] = "NO_PRIOR_PERIOD"
            entry["base_value"] = 0.0
            entry["note"] = "baseline is 0.0; percentage growth undefined"
            entry["formula"] = "not computed — division by zero"
        else:
            current, base = row["actual_spend"], base_row["actual_spend"]
            growth = (current - base) / base * 100
            entry["base_value"] = base
            entry["formula"] = "({} - {}) / {} * 100".format(current, base, base)
            entry["growth_pct"] = round(growth, 1)
            entry["status"] = "COMPUTED"

        results.append(entry)

    return results


def write_output(results, path):
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(results)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--ward", default=None)
    parser.add_argument("--category", default=None)
    # deliberately NOT required and with no default: absence must be refused,
    # not silently resolved to MoM
    parser.add_argument("--growth-type", dest="growth_type", default=None)
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
    except (OSError, ValueError) as error:
        print("ERROR: cannot read {}: {}".format(args.input, error), file=sys.stderr)
        sys.exit(1)

    try:
        results = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except (AggregationRefused, GrowthTypeNotSpecified, EmptySelection) as refusal:
        print(str(refusal), file=sys.stderr)
        sys.exit(2)

    write_output(results, args.output)

    computed = [r for r in results if r["status"] == "COMPUTED"]
    print("{} | {} | {}".format(results[0]["ward"], results[0]["category"],
                                args.growth_type))
    print("periods: {} | computed: {} | not computed: {}".format(
        len(results), len(computed), len(results) - len(computed)))
    for row in results:
        if row["status"] != "COMPUTED":
            print("  {} {:<16} {}".format(row["period"], row["status"], row["note"]))
    if args.growth_type == "YoY":
        print("\nNOTE: YoY is NOT COMPUTABLE on this dataset — it covers 2024 only.")
    print("\nWritten to {}".format(args.output))


if __name__ == "__main__":
    main()
