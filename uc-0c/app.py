"""
UC-0C — Number That Looks Right
Single-slice MoM/YoY growth calculator for ward_budget.csv.
Implements agents.md enforcement and skills.md contracts.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ("MoM", "YoY")
OUTPUT_FIELDS = ["ward", "category", "period", "budgeted_amount", "actual_spend", "growth_pct", "formula", "flag"]


def normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def load_dataset(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            missing = [col for col in REQUIRED_COLUMNS if col not in (reader.fieldnames or [])]
            if missing:
                print(f"Input CSV is missing required columns: {missing}", file=sys.stderr)
                sys.exit(1)
            rows = list(reader)
    except OSError as exc:
        print(f"Cannot read input file {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    null_rows = []
    for row in rows:
        raw = (row.get("actual_spend") or "").strip()
        if not raw:
            row["actual_spend"] = None
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "reason": (row.get("notes") or "").strip() or "(no reason given in notes)",
                }
            )
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    norm_ward = normalize(ward)
    norm_cat = normalize(category)

    if norm_ward in {"all", ""} or norm_cat in {"all", ""}:
        print("REFUSAL: aggregating across wards/categories is not permitted. "
              "Request exactly one ward and one category.", file=sys.stderr)
        sys.exit(2)

    matched = [r for r in rows if normalize(r["ward"]) == norm_ward and normalize(r["category"]) == norm_cat]
    if not matched:
        available_wards = sorted({r["ward"] for r in rows})
        available_categories = sorted({r["category"] for r in rows})
        print(f"REFUSAL: no rows match ward={ward!r}, category={category!r}.", file=sys.stderr)
        print(f"Valid wards: {available_wards}", file=sys.stderr)
        print(f"Valid categories: {available_categories}", file=sys.stderr)
        sys.exit(2)

    matched.sort(key=lambda r: r["period"])
    history = {(r["ward"], r["category"], r["period"]): r for r in rows}
    table = []

    for index, row in enumerate(matched):
        current_raw = row["actual_spend"]
        flag_parts = []
        formula = ""
        growth_pct = ""

        if growth_type == "MoM":
            if index == 0:
                base_row, base_label = None, "no prior month in slice"
            else:
                prev = matched[index - 1]
                base_row, base_label = prev, f"prior month {prev['period']}"
            base_raw = base_row["actual_spend"] if base_row else None
        else:
            year, month = row["period"].split("-")
            prior_period = f"{int(year) - 1:04d}-{month}"
            base_row = history.get((row["ward"], row["category"], prior_period))
            base_raw = base_row["actual_spend"] if base_row else None
            base_label = f"same month prior year {prior_period}"

        if current_raw is None:
            reason = (row.get("notes") or "").strip() or "(no reason given in notes)"
            flag_parts.append(f"NULL actual_spend — not computed; reason: {reason}")
        elif base_raw is None and base_row is not None and base_row.get("_was_null"):
            flag_parts.append(f"prior period {base_row['period']} actual_spend is NULL — cannot compute")
        elif base_raw is None:
            flag_parts.append(f"cannot compute {growth_type}: {base_label}")
        else:
            current_val = float(current_raw)
            base_val = float(base_raw) if isinstance(base_raw, str) else base_raw
            pct = (current_val - float(base_raw)) / float(base_raw) * 100.0
            sign = "+" if pct >= 0 else "-"
            growth_pct = f"{sign}{abs(pct):.1f}%"
            formula = f"({current_val:g} - {float(base_raw):g}) / {float(base_raw):g} * 100 = {growth_pct}"

        out_row = dict(row)
        if row.get("_was_null"):
            out_row["actual_spend"] = "NULL"
        out_row["growth_pct"] = growth_pct
        out_row["formula"] = formula
        out_row["flag"] = "; ".join(flag_parts)
        table.append(out_row)

    return table


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exactly one ward name (never 'all')")
    parser.add_argument("--category", help="Exactly one category name (never 'all')")
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY — will NOT be guessed")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("REFUSAL: --growth-type was not specified. I will not guess. "
              f"Please provide one of: {', '.join(GROWTH_TYPES)}.", file=sys.stderr)
        sys.exit(2)
    if args.growth_type not in GROWTH_TYPES:
        print(f"REFUSAL: unknown growth type {args.growth_type!r}. "
              f"Valid options: {', '.join(GROWTH_TYPES)}.", file=sys.stderr)
        sys.exit(2)
    if not args.ward or not args.category:
        print("REFUSAL: both --ward and --category must name exactly one value each "
              "(aggregation across wards/categories is not permitted).", file=sys.stderr)
        sys.exit(2)

    rows, null_rows = load_dataset(args.input)

    print(f"Dataset loaded: {len(rows)} rows.")
    print(f"Null actual_spend rows found BEFORE computing: {len(null_rows)}")
    for entry in null_rows:
        print(f"  - {entry['period']} | {entry['ward']} | {entry['category']} | reason: {entry['reason']}")

    for row in rows:
        row["_was_null"] = row["actual_spend"] is None

    table = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(table)

    flagged = sum(1 for r in table if r["flag"])
    print(f"Wrote {len(table)} rows ({args.ward} / {args.category} / {args.growth_type}) to {args.output}; "
          f"{flagged} rows carry flags.")


if __name__ == "__main__":
    main()
