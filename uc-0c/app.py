"""
UC-0C app.py — Number That Looks Right.

Computes MoM or YoY growth in actual_spend for a single (ward, category)
slice of the ward budget CSV.

Enforcement (see agents.md):
  * Never aggregate across wards or categories.
  * Flag every null actual_spend row — never impute.
  * Show the formula on every output row.
  * Refuse if --growth-type is missing or unsupported.
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Optional


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]

SUPPORTED_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(path: str) -> list[dict]:
    """Read CSV, validate columns, report nulls to stderr, return rows."""
    try:
        f = open(path, newline="", encoding="utf-8")
    except OSError as e:
        sys.exit(f"ERROR: cannot open input file '{path}': {e}")

    with f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(
                f"ERROR: input CSV is missing required columns: {missing}. "
                f"Found: {reader.fieldnames}"
            )
        rows = list(reader)

    null_rows = [
        {
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "notes": r["notes"],
        }
        for r in rows
        if r["actual_spend"] is None or r["actual_spend"].strip() == ""
    ]

    print(
        f"[load_dataset] loaded {len(rows)} rows from {path}; "
        f"null actual_spend count = {len(null_rows)}",
        file=sys.stderr,
    )
    for nr in null_rows:
        print(
            f"[load_dataset] NULL: {nr['period']} | {nr['ward']} | "
            f"{nr['category']} | reason: {nr['notes']}",
            file=sys.stderr,
        )
    return rows


def _parse_spend(value: str) -> Optional[float]:
    if value is None or value.strip() == "":
        return None
    return float(value)


def _prior_period(period: str, growth_type: str) -> str:
    """Return the period key required by the given growth_type."""
    year, month = period.split("-")
    y, m = int(year), int(month)
    if growth_type == "MoM":
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    elif growth_type == "YoY":
        y -= 1
    else:  # pragma: no cover — guarded upstream
        raise ValueError(f"unsupported growth_type: {growth_type}")
    return f"{y:04d}-{m:02d}"


def compute_growth(
    rows: list[dict], ward: str, category: str, growth_type: str
) -> list[dict]:
    """Return per-period growth rows for one (ward, category) slice."""
    if growth_type not in SUPPORTED_GROWTH_TYPES:
        sys.exit(
            f"ERROR: --growth-type must be one of {sorted(SUPPORTED_GROWTH_TYPES)}; "
            f"got '{growth_type}'. Refusing to guess."
        )

    slice_rows = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    if not slice_rows:
        sys.exit(
            f"ERROR: no rows found for ward='{ward}' and category='{category}'. "
            f"Refusing to aggregate or substitute."
        )

    # Index by period for prior-period lookups.
    by_period = {r["period"]: r for r in slice_rows}
    slice_rows.sort(key=lambda r: r["period"])

    out: list[dict] = []
    for r in slice_rows:
        period = r["period"]
        spend = _parse_spend(r["actual_spend"])
        note = r["notes"].strip() if r["notes"] else ""

        if spend is None:
            out.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "NULL",
                    "growth_pct": "NULL",
                    "formula": f"{growth_type} = n/a — current period actual_spend is null",
                    "note": f"flagged: {note}" if note else "flagged: null actual_spend",
                }
            )
            continue

        prior_key = _prior_period(period, growth_type)
        prior_row = by_period.get(prior_key)
        prior_spend = _parse_spend(prior_row["actual_spend"]) if prior_row else None

        if prior_spend is None or prior_spend == 0:
            reason = (
                "prior period not in dataset"
                if prior_row is None
                else (
                    "prior period actual_spend is null"
                    if prior_spend is None
                    else "prior period actual_spend is zero (division undefined)"
                )
            )
            out.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{spend:.1f}",
                    "growth_pct": "NULL",
                    "formula": f"{growth_type} = n/a — {reason}",
                    "note": f"prior period key: {prior_key}",
                }
            )
            continue

        growth = (spend - prior_spend) / prior_spend * 100.0
        out.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{spend:.1f}",
                "growth_pct": f"{growth:+.1f}%",
                "formula": (
                    f"{growth_type} = ({spend:.1f} - {prior_spend:.1f}) "
                    f"/ {prior_spend:.1f} * 100"
                ),
                "note": f"prior period: {prior_key}",
            }
        )
    return out


def _write_output(path: str, out_rows: list[dict]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_pct",
        "formula",
        "note",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="UC-0C — per-ward per-category growth analyzer."
    )
    p.add_argument("--input", required=True, help="Path to ward_budget.csv")
    p.add_argument("--ward", required=True, help="Exact ward name, e.g. 'Ward 1 – Kasba'")
    p.add_argument("--category", required=True, help="Exact category name")
    p.add_argument(
        "--growth-type",
        required=True,
        choices=sorted(SUPPORTED_GROWTH_TYPES),
        help="MoM or YoY — refuses to default.",
    )
    p.add_argument("--output", required=True, help="Path to write growth_output.csv")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    rows = load_dataset(args.input)
    out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    _write_output(args.output, out_rows)

    print(
        f"[app] wrote {len(out_rows)} rows to {args.output} "
        f"for ward='{args.ward}', category='{args.category}', "
        f"growth_type={args.growth_type}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
