"""
UC-0C — Number That Looks Right
Implements agents.md + skills.md: load_dataset, compute_growth.

Per-ward per-category growth table with explicit formulas; null actual_spend rows flagged
with notes; --growth-type required (never guessed).
"""
import argparse
import csv
import os
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

REQUIRED_COLUMNS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)

MOM_FORMULA = (
    "MoM growth % = ((actual_spend_current − actual_spend_previous) ÷ actual_spend_previous) × 100"
)
YOY_FORMULA = (
    "YoY growth % = ((actual_spend_current − actual_spend_same_month_prior_year) "
    "÷ actual_spend_same_month_prior_year) × 100"
)


def _parse_actual_spend(raw: str) -> Optional[float]:
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return float(str(raw).strip())
    except ValueError:
        return None


def load_dataset(path: str) -> Dict[str, Any]:
    """
    skills.md load_dataset: read CSV, validate columns, report nulls before returning.
    """
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row")
            header = [h.strip() if h else h for h in reader.fieldnames]
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required columns: {missing}; got {list(reader.fieldnames)}")

            rows: List[Dict[str, str]] = []
            for row in reader:
                rows.append(dict(row))

    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding, e.object, e.start, e.end, f"File must be UTF-8: {path}"
        ) from e

    if not rows:
        raise ValueError("CSV contains no data rows")

    null_rows: List[Dict[str, str]] = []
    for row in rows:
        spend = _parse_actual_spend(row.get("actual_spend", ""))
        if spend is None:
            null_rows.append(
                {
                    "period": row.get("period", "").strip(),
                    "ward": row.get("ward", "").strip(),
                    "category": row.get("category", "").strip(),
                    "notes": row.get("notes", "").strip(),
                }
            )

    return {
        "rows": rows,
        "null_report": {"count": len(null_rows), "rows": null_rows},
    }


def _normalize_growth_type(raw: str) -> str:
    t = raw.strip().upper().replace("-", "").replace("_", "")
    if t == "MOM":
        return "MoM"
    if t == "YOY":
        return "YoY"
    raise ValueError(
        f"Unsupported --growth-type {raw!r}. Use MoM or YoY."
    )


def _period_key(period: str) -> Tuple[int, int]:
    """YYYY-MM -> (year, month) for sorting and YoY lookup."""
    parts = period.strip().split("-", 2)
    if len(parts) != 2:
        raise ValueError(f"Bad period (expected YYYY-MM): {period!r}")
    y, m = int(parts[0]), int(parts[1])
    return y, m


def _shift_year(period: str, delta_years: int) -> str:
    y, m = _period_key(period)
    y2 = y + delta_years
    return f"{y2:04d}-{m:02d}"


def compute_growth(
    loaded: Dict[str, Any],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    skills.md compute_growth: one ward/category, ordered periods, formula + growth or FLAG.
    """
    gt = _normalize_growth_type(growth_type)
    w, c = ward.strip(), category.strip()
    rows_all = loaded["rows"]
    series = [r for r in rows_all if r.get("ward", "").strip() == w and r.get("category", "").strip() == c]
    if not series:
        raise ValueError(f"No rows for ward={ward!r} category={category!r}")

    series.sort(key=lambda r: _period_key(r["period"]))
    index_by_period = {r["period"].strip(): i for i, r in enumerate(series)}

    out: List[Dict[str, str]] = []
    for i, row in enumerate(series):
        period = row["period"].strip()
        notes = (row.get("notes") or "").strip()
        curr = _parse_actual_spend(row.get("actual_spend", ""))
        budgeted = (row.get("budgeted_amount") or "").strip()

        base = {
            "period": period,
            "ward": w,
            "category": c,
            "budgeted_amount": budgeted,
            "actual_spend": "" if curr is None else f"{curr:g}",
            "growth_pct": "",
            "formula": "",
            "notes": notes,
        }

        if curr is None:
            base["growth_pct"] = "FLAG"
            base["formula"] = (
                "Growth not computed: actual_spend is null — reason from notes column: "
                + (notes or "(empty)")
            )
            out.append(base)
            continue

        if gt == "MoM":
            base["formula"] = MOM_FORMULA
            if i == 0:
                base["growth_pct"] = "n/a"
                base["formula"] = MOM_FORMULA + " — no prior month in this ward/category series."
                out.append(base)
                continue
            prev_row = series[i - 1]
            prev = _parse_actual_spend(prev_row.get("actual_spend", ""))
            if prev is None:
                base["growth_pct"] = "FLAG"
                base["formula"] = (
                    MOM_FORMULA
                    + " — not computed because prior month actual_spend is null: "
                    + (prev_row.get("notes") or "(no note)").strip()
                )
                out.append(base)
                continue
            if prev == 0:
                base["growth_pct"] = "FLAG"
                base["formula"] = MOM_FORMULA + " — not computed (previous month spend is 0)."
                out.append(base)
                continue
            pct = (curr - prev) / prev * 100.0
            sign = "+" if pct > 0 else ""
            base["growth_pct"] = f"{sign}{pct:.1f}%"
            out.append(base)
            continue

        # YoY
        base["formula"] = YOY_FORMULA
        prior_period = _shift_year(period, -1)
        j = index_by_period.get(prior_period)
        if j is None:
            base["growth_pct"] = "n/a"
            base["formula"] = (
                YOY_FORMULA
                + f" — no row for prior-year period {prior_period} in dataset; YoY not computed."
            )
            out.append(base)
            continue
        prev_row = series[j]
        prev = _parse_actual_spend(prev_row.get("actual_spend", ""))
        if prev is None:
            base["growth_pct"] = "FLAG"
            base["formula"] = (
                YOY_FORMULA
                + " — not computed because prior-year same month actual_spend is null: "
                + (prev_row.get("notes") or "").strip()
            )
            out.append(base)
            continue
        if prev == 0:
            base["growth_pct"] = "FLAG"
            base["formula"] = YOY_FORMULA + " — not computed (prior-year month spend is 0)."
            out.append(base)
            continue
        pct = (curr - prev) / prev * 100.0
        sign = "+" if pct > 0 else ""
        base["growth_pct"] = f"{sign}{pct:.1f}%"
        out.append(base)

    return out


def _write_output(path: str, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_pct",
        "formula",
        "notes",
    ]
    out_path = path
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def _print_null_report(null_report: Dict[str, Any]) -> None:
    print(
        f"[load_dataset] Null actual_spend rows in full dataset: {null_report['count']}",
        file=sys.stderr,
    )
    for r in null_report["rows"]:
        label = f"{r['period']} · {r['ward']} · {r['category']}"
        note = r.get("notes") or ""
        print(f"  — {label} | notes: {note}", file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="UC-0C ward/category growth (per agents.md).")
    p.add_argument(
        "--input",
        default=os.path.join("..", "data", "budget", "ward_budget.csv"),
        help="Path to ward_budget.csv",
    )
    p.add_argument("--ward", required=True, help="Single ward name (exact string in CSV)")
    p.add_argument("--category", required=True, help="Single category (exact string in CSV)")
    p.add_argument(
        "--growth-type",
        required=True,
        metavar="MoM|YoY",
        help="Required: MoM (month-over-month) or YoY (year-over-year). Omitting is an error.",
    )
    p.add_argument(
        "--output",
        default="growth_output.csv",
        help="Output CSV path (default: growth_output.csv)",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    inp = os.path.abspath(args.input)
    try:
        loaded = load_dataset(inp)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    _print_null_report(loaded["null_report"])

    try:
        result = compute_growth(loaded, args.ward, args.category, args.growth_type)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    out_abs = os.path.abspath(args.output)
    _write_output(out_abs, result)
    print(f"Wrote {len(result)} rows to {out_abs}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
