"""
UC-0C app.py — Number That Looks Right
Built from agents.md (role / intent / context / enforcement) and skills.md
(load_dataset, compute_growth). Standard library only.

Enforcement rule -> code:
  never aggregate; refuse wildcards       -> _require_scope(), compute_growth()
  null report before computing            -> load_dataset() NULL REPORT, main()
  formula on every row                    -> compute_growth() 'formula' column
  first period NO_PRIOR                   -> compute_growth()
  null poisons next period (PRIOR_NULL)   -> compute_growth()
  --growth-type explicit MoM/YoY only     -> _require_growth_type()
  YoY honest: NO_PRIOR_YEAR, no fallback  -> _prior_period(), compute_growth()
  exact ward/category match, list valid   -> compute_growth()
  no summary/total row                    -> compute_growth() returns per-period rows only
  refusal = ERROR on stderr, exit 1, no output file -> main()
"""
import argparse
import csv
import os
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
OUTPUT_COLUMNS = [
    "period", "ward", "category", "budgeted_amount", "actual_spend",
    "prior_period", "prior_actual", "formula", "growth_pct", "status", "notes",
]
GROWTH_TYPES = ("MoM", "YoY")
WILDCARDS = {"", "all", "total", "totals", "combined", "city-wide", "citywide", "*", "any", "every", "overall"}
_PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class Refusal(Exception):
    """Raised whenever the enforcement rules say refuse rather than guess."""


# --------------------------------------------------------------------------
# Skill 1: load_dataset  (skills.md)
# --------------------------------------------------------------------------
def load_dataset(path: str, report=None) -> dict:
    """
    Read and validate ward_budget.csv. Prints a NULL REPORT via `report`
    (default: stderr) before returning so nulls are visible pre-computation.
    """
    report = report if report is not None else (lambda m: print(m, file=sys.stderr))

    if not os.path.isfile(path):
        raise Refusal(f"input file not found: {path}")
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            if [h.strip() for h in header] != REQUIRED_COLUMNS:
                raise Refusal(
                    f"unexpected columns {header}; required exactly {REQUIRED_COLUMNS}"
                )
            raw_rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        raise Refusal(f"could not read {path}: {e}")

    rows, null_rows = [], []
    for n, r in enumerate(raw_rows, start=2):  # line 2 = first data row
        row = {k: (v or "").strip() for k, v in r.items()}
        if not _PERIOD_RE.match(row["period"]):
            raise Refusal(f"line {n}: period '{row['period']}' is not YYYY-MM")
        # Keep the source text for display so amounts are never reformatted.
        row["budgeted_amount_raw"] = row["budgeted_amount"]
        row["actual_spend_raw"] = row["actual_spend"]
        try:
            row["budgeted_amount"] = float(row["budgeted_amount"])
        except ValueError:
            raise Refusal(f"line {n}: budgeted_amount '{row['budgeted_amount']}' is blank or non-numeric")
        if row["actual_spend"] == "":
            row["actual_spend"] = None
            null_rows.append({
                "period": row["period"], "ward": row["ward"], "category": row["category"],
                "notes": row["notes"] or "no reason given in notes",
            })
        else:
            try:
                row["actual_spend"] = float(row["actual_spend"])
            except ValueError:
                raise Refusal(f"line {n}: actual_spend '{row['actual_spend']}' is non-numeric (not blank)")
        rows.append(row)

    dataset = {
        "rows": rows,
        "wards": sorted({r["ward"] for r in rows}),
        "categories": sorted({r["category"] for r in rows}),
        "periods": sorted({r["period"] for r in rows}),
        "null_rows": null_rows,
        "null_count": len(null_rows),
    }

    report(f"NULL REPORT: {len(null_rows)} row(s) with blank actual_spend out of {len(rows)} rows")
    for nr in null_rows:
        report(f"  NULL  {nr['period']}  {nr['ward']}  {nr['category']}  — {nr['notes']}")
    return dataset


# --------------------------------------------------------------------------
# Skill 2: compute_growth  (skills.md)
# --------------------------------------------------------------------------
def _require_scope(name: str, value) -> str:
    v = (value or "").strip()
    if v.lower() in WILDCARDS:
        plural = "categories" if name == "category" else f"{name}s"
        raise Refusal(
            f"--{name} is missing or a wildcard ('{value}'). Growth is computed for ONE {name} "
            f"at a time; aggregation across {plural} is not permitted."
        )
    return v


def _require_growth_type(value) -> str:
    v = (value or "").strip()
    if v not in GROWTH_TYPES:
        raise Refusal(
            f"--growth-type must be given explicitly as one of {list(GROWTH_TYPES)} "
            f"(got '{value}'). No default is assumed."
        )
    return v


def _prior_period(period: str, growth_type: str) -> str:
    year, month = int(period[:4]), int(period[5:])
    if growth_type == "MoM":
        if month == 1:
            year, month = year - 1, 12
        else:
            month -= 1
    else:  # YoY
        year -= 1
    return f"{year:04d}-{month:02d}"


def _fmt(x) -> str:
    """Render a float compactly; used only where no source text exists."""
    return f"{x:g}"


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    ward = _require_scope("ward", ward)
    category = _require_scope("category", category)
    growth_type = _require_growth_type(growth_type)

    if ward not in dataset["wards"]:
        raise Refusal(f"ward '{ward}' not found. Valid wards: {dataset['wards']}")
    if category not in dataset["categories"]:
        raise Refusal(f"category '{category}' not found. Valid categories: {dataset['categories']}")

    scoped = sorted(
        (r for r in dataset["rows"] if r["ward"] == ward and r["category"] == category),
        key=lambda r: r["period"],
    )
    if not scoped:
        raise Refusal(f"no rows for ward '{ward}' and category '{category}'")
    by_period = {r["period"]: r for r in scoped}

    table = []
    for r in scoped:
        period, actual = r["period"], r["actual_spend"]
        prior_p = _prior_period(period, growth_type)
        prior = by_period.get(prior_p)
        out = {
            "period": period, "ward": ward, "category": category,
            "budgeted_amount": r["budgeted_amount_raw"],
            "actual_spend": r["actual_spend_raw"],
            "prior_period": prior_p,
            "prior_actual": "",
            "formula": "",
            "growth_pct": "",
            "status": "",
            "notes": r["notes"],
        }

        if actual is None:
            out["status"] = "NULL"
            out["formula"] = f"n/a — actual_spend is null for {period}: {r['notes'] or 'no reason given in notes'}"
        elif prior is None:
            if growth_type == "YoY":
                out["status"] = "NO_PRIOR_YEAR"
                out["formula"] = f"n/a — {prior_p} (period minus 12 months) is outside the dataset"
            else:
                out["status"] = "NO_PRIOR"
                out["formula"] = "n/a — no prior period"
        elif prior["actual_spend"] is None:
            out["status"] = "PRIOR_NULL"
            out["formula"] = f"n/a — prior period {prior_p} actual_spend is null: {prior['notes'] or 'no reason given in notes'}"
        else:
            p = prior["actual_spend"]
            p_txt, a_txt = prior["actual_spend_raw"], r["actual_spend_raw"]
            out["prior_actual"] = p_txt
            if p == 0:
                out["status"] = "DIV_ZERO"
                out["formula"] = f"n/a — prior actual_spend for {prior_p} is 0"
            else:
                growth = (actual - p) / p * 100
                out["status"] = "OK"
                out["formula"] = f"({a_txt} - {p_txt}) / {p_txt} * 100"
                out["growth_pct"] = f"{growth:.1f}"
        table.append(out)

    # Enforcement: exactly one ward, one category, no aggregate row.
    assert {t["ward"] for t in table} == {ward} and {t["category"] for t in table} == {category}
    return table


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Exact ward string, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", help="Exact category string, e.g. 'Roads & Pothole Repair'")
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY (required, no default)")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        table = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except Refusal as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(table)

    counts = {}
    for t in table:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    print(
        f"Done. {len(table)} rows written to {args.output} for ward '{args.ward}' / "
        f"category '{args.category}' ({args.growth_type}). Status counts: {counts}"
    )


if __name__ == "__main__":
    main()
