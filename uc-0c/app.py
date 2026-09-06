"""
UC-0C app.py — Number That Looks Right
Build guided by agents.md (RICE framework) and skills.md.

Failure modes targeted:
  - Wrong aggregation level -> refuses to mix wards/categories; per-single ward+category only
  - Silent null handling    -> every null actual_spend flagged with notes reason BEFORE compute
  - Formula assumption     -> growth type must be explicitly requested; formula shown per row
"""
import argparse
import csv
import os
import sys
from typing import Dict, List

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
# MoM is the ONLY supported growth type for this dataset (single year of data).
# YoY is intentionally unsupported and will be refused.
SUPPORTED_GROWTH_TYPES = ["MoM"]


class RefusalError(Exception):
    """Raised when the system must refuse rather than guess."""


# ---------------------------------------------------------------------------
# Skill: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(input_path: str) -> Dict[str, object]:
    """Read + validate the CSV; report nulls BEFORE any computation; return rows."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    with open(input_path, mode="r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError("Empty CSV — no columns found.")
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            raise ValueError(
                f"CSV is missing required column(s): {missing_cols}. "
                f"Expected: {EXPECTED_COLUMNS}")
        rows = [dict(r) for r in reader]

    null_rows = [
        r for r in rows if r.get("actual_spend") is None
        or str(r.get("actual_spend", "")).strip() == ""
    ]

    if null_rows:
        print("[null warning] {n} rows have NULL actual_spend — flagged, not computed:"
              .format(n=len(null_rows)))
        for r in null_rows:
            reason = (r.get("notes") or "").strip() or "no reason provided"
            print(f"  {r['period']} | {r['ward']} | {r['category']} | reason: {reason}")

    wards = sorted({r["ward"].strip() for r in rows})
    categories = sorted({r["category"].strip() for r in rows})
    return {"rows": rows, "null_rows": null_rows, "wards": wards, "categories": categories}


def _as_float(value) -> Dict[str, object]:
    try:
        if value is None or str(value).strip() == "":
            return {"ok": False, "value": None}
        return {"ok": True, "value": float(str(value).strip())}
    except ValueError:
        return {"ok": False, "value": None}


# ---------------------------------------------------------------------------
# Skill: compute_growth
# ---------------------------------------------------------------------------
def _month_delta(period: str, months: int) -> str | None:
    """Shift a YYYY-MM string by +-months."""
    year, month = period.split("-")
    y, m = int(year), int(month) + months
    while m < 1:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return f"{y:04d}-{m:02d}"


def compute_growth(rows: List[dict], ward: str, category: str,
                   growth_type: str) -> List[dict]:
    """Per-period growth table for a single ward + category with formula shown.

    UC-0C supports MoM only. growth_type has already been validated as MoM by
    _validate_scope; this branch exists for future extension.
    """
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        raise RefusalError(
            f"Unsupported growth type '{growth_type}'. Supported: {SUPPORTED_GROWTH_TYPES}. "
            "Refuse rather than guess.")

    ward_rows = [r for r in rows if r["ward"].strip() == ward
                 and r["category"].strip() == category]
    ward_rows.sort(key=lambda r: r["period"])

    index = {}
    for r in ward_rows:
        index[r["period"]] = r

    output: List[dict] = []
    delta = -1 if growth_type == "MoM" else -12

    for r in ward_rows:
        period = r["period"]
        cur = _as_float(r["actual_spend"])
        prev_period = _month_delta(period, delta)
        prev_row = index.get(prev_period)
        prev = _as_float(prev_row["actual_spend"]) if prev_row else {"ok": False, "value": None}

        row = {
            "period": period,
            "ward": r["ward"].strip(),
            "category": r["category"].strip(),
            "budgeted_amount": r["budgeted_amount"].strip(),
            "actual_spend": r["actual_spend"].strip(),
            "growth_type": growth_type,
            "previous_period": prev_period if prev_row else "n/a",
            "growth_pct": "NULL",
            "formula": "",
            "flag": "",
        }

        if not cur["ok"]:
            row["flag"] = "not computed — actual_spend is NULL"
            reason = (r.get("notes") or "").strip()
            if reason:
                row["flag"] += f"; {reason}"
        elif not prev_row:
            row["flag"] = f"not computed — no {growth_type} comparison period ({prev_period}) in dataset"
        elif not prev["ok"]:
            row["flag"] = (f"not computed — previous period {prev_period} has NULL "
                           "actual_spend")
        elif prev["value"] == 0:
            row["flag"] = f"not computed — previous period {prev_period} value is 0 (divide by zero)"
        else:
            pct = (cur["value"] - prev["value"]) / prev["value"] * 100
            formatted = f"{pct:+.1f}"
            row["growth_pct"] = formatted
            row["formula"] = (f"(({cur['value']:g}-{prev['value']:g})/"
                              f"{prev['value']:g})*100 = {formatted}")
        output.append(row)

    return output


# ---------------------------------------------------------------------------
# Refusals per enforcement rules
# ---------------------------------------------------------------------------
def _validate_scope(args, dataset: Dict[str, object]):
    """Enforce zero implicit defaults: refuse on ANY missing calculation parameter."""
    missing, hints = [], []
    if not args.ward:
        missing.append("--ward")
        hints.append("--ward (e.g. 'Ward 1 – Kasba')")
    if not args.category:
        missing.append("--category")
        hints.append("--category (e.g. 'Roads & Pothole Repair')")
    if not args.growth_type:
        missing.append("--growth-type")
        hints.append(f"--growth-type (e.g. {SUPPORTED_GROWTH_TYPES[0]})")
    if missing:
        raise RefusalError(
            "REFUSED: missing required parameter(s): "
            + ", ".join(missing)
            + ". NO implicit defaults permitted — please specify "
            + ", ".join(hints) + " and re-run.")
    if args.growth_type not in SUPPORTED_GROWTH_TYPES:
        raise RefusalError(
            f"REFUSED: unsupported growth type '{args.growth_type}'. "
            f"Valid choices: {SUPPORTED_GROWTH_TYPES}. Please re-run with "
            f"--growth-type {SUPPORTED_GROWTH_TYPES[0]}.")
    if args.ward not in dataset["wards"]:
        raise RefusalError(
            f"REFUSED: unknown ward '{args.ward}'. Valid wards: "
            + ", ".join(dataset["wards"]))
    if args.category not in dataset["categories"]:
        raise RefusalError(
            f"REFUSED: unknown category '{args.category}'. Valid categories: "
            + ", ".join(dataset["categories"]))
    combo = [r for r in dataset["rows"]
             if r["ward"].strip() == args.ward and r["category"].strip() == args.category]
    if not combo:
        raise RefusalError(
            f"REFUSED: no data rows exist for '{args.ward}' + '{args.category}' — "
            "refuse rather than emit an empty table.")


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Single ward (required; aggregation refused)")
    parser.add_argument("--category", help="Single category (required; aggregation refused)")
    parser.add_argument("--growth-type", help="MoM or YoY (required; never guessed)")
    parser.add_argument("--output", default="growth_output.csv",
                        help="Path to write output table")
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        _validate_scope(args, dataset)

        rows = [r for r in dataset["rows"]
                if r["ward"].strip() == args.ward and r["category"].strip() == args.category]
        table = compute_growth(rows, args.ward, args.category, args.growth_type)

        out_dir = os.path.dirname(args.output)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend",
                      "growth_type", "previous_period", "growth_pct", "formula", "flag"]
        with open(args.output, mode="w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(table)

        computable = [t for t in table if t["growth_pct"] != "NULL"]
        print(f"Done. Wrote {len(table)} rows to {args.output}")
        print(f"  scope          : {args.ward} | {args.category} | {args.growth_type}")
        print(f"  computed       : {len(computable)} periods")
        print(f"  flagged NULL   : {len(table) - len(computable)} periods (see 'flag' column)")
    except (RefusalError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()