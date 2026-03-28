"""
UC-0C — per-ward per-category budget growth (MoM / YoY) with explicit formulas.
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

REQUIRED_COLUMNS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)

GROWTH_TYPES = ("MoM", "YoY")


def _norm_label(s: str) -> str:
    """Normalize dash variants so CLI args match CSV labels (e.g. en dash vs hyphen)."""
    t = s.strip()
    for ch in ("\u2013", "\u2014", "\u2212"):
        t = t.replace(ch, "-")
    return t


class LoadDatasetError(Exception):
    """Invalid path, schema, or unreadable CSV."""


class ComputeGrowthError(Exception):
    """Unsupported growth type, missing scope, or invalid growth request."""


@dataclass
class NullRowReport:
    period: str
    ward: str
    category: str
    notes: str


@dataclass
class LoadDatasetResult:
    rows: list[dict[str, Any]]
    null_rows: list[NullRowReport] = field(default_factory=list)


def load_dataset(
    csv_path: str | Path,
    *,
    encoding: str = "utf-8",
    city_wide_aggregate: bool = False,
) -> LoadDatasetResult:
    """
    Skill: load_dataset — read CSV, validate columns, report null actual_spend rows before returning data.
    """
    if city_wide_aggregate:
        raise LoadDatasetError(
            "Refusing to load or merge data into a single city-wide aggregate."
        )

    path = Path(csv_path)
    if not path.exists():
        raise LoadDatasetError(f"Input path does not exist: {path}")
    if path.is_dir():
        raise LoadDatasetError(
            "Input path is a directory; expected a single CSV file path."
        )
    if not path.is_file():
        raise LoadDatasetError(f"Input path is not a readable file: {path}")

    try:
        raw = path.read_text(encoding=encoding)
    except OSError as e:
        raise LoadDatasetError(f"Cannot read file {path}: {e}") from e
    except UnicodeDecodeError as e:
        raise LoadDatasetError(f"File is not valid {encoding} text: {e}") from e

    lines = raw.splitlines()
    if not lines:
        raise LoadDatasetError("CSV file is empty.")

    reader = csv.DictReader(lines)
    if reader.fieldnames is None:
        raise LoadDatasetError("CSV has no header row.")

    header = [h.strip() if h else h for h in reader.fieldnames]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing:
        raise LoadDatasetError(
            "Missing required column(s): "
            + ", ".join(missing)
            + f". Required: {', '.join(REQUIRED_COLUMNS)}."
        )

    rows: list[dict[str, Any]] = []
    null_rows: list[NullRowReport] = []

    for row in reader:
        rec = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        period = rec.get("period", "")
        ward = rec.get("ward", "")
        category = rec.get("category", "")
        spend_raw = rec.get("actual_spend", "")
        notes = rec.get("notes") or ""

        if spend_raw is None or (isinstance(spend_raw, str) and spend_raw.strip() == ""):
            rec["actual_spend"] = None
            null_rows.append(
                NullRowReport(
                    period=str(period),
                    ward=str(ward),
                    category=str(category),
                    notes=str(notes),
                )
            )
        else:
            try:
                rec["actual_spend"] = float(spend_raw)
            except (TypeError, ValueError) as e:
                raise LoadDatasetError(
                    f"Non-numeric actual_spend for {period} / {ward} / {category}: {spend_raw!r}"
                ) from e

        try:
            rec["budgeted_amount"] = float(rec["budgeted_amount"])
        except (TypeError, ValueError, KeyError) as e:
            raise LoadDatasetError(
                f"Invalid budgeted_amount for {period} / {ward} / {category}."
            ) from e

        rows.append(rec)

    return LoadDatasetResult(rows=rows, null_rows=null_rows)


def _prev_month(period: str) -> str | None:
    y_s, m_s = period.split("-", 1)
    y, m = int(y_s), int(m_s)
    if m == 1:
        return f"{y - 1:04d}-12"
    return f"{y:04d}-{m - 1:02d}"


def _prev_year_month(period: str) -> str:
    y_s, m_s = period.split("-", 1)
    y, m = int(y_s), int(m_s)
    return f"{y - 1:04d}-{m:02d}"


def _format_pct(value: float) -> str:
    return f"{value:+.1f}%"


def compute_growth(
    rows: list[dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict[str, Any]]:
    """
    Skill: compute_growth — one ward, one category, explicit growth_type; per-period rows with formula.
    """
    if not growth_type or not str(growth_type).strip():
        raise ComputeGrowthError(
            "growth_type is required (e.g. MoM or YoY). Refusing to guess."
        )

    gt = growth_type.strip()
    # canonical match
    upper = gt.upper()
    if upper == "MOM":
        canonical: Literal["MoM", "YoY"] = "MoM"
    elif upper == "YOY":
        canonical = "YoY"
    elif gt in GROWTH_TYPES:
        canonical = gt  # type: ignore[assignment]
    else:
        raise ComputeGrowthError(
            f"Unsupported growth_type {growth_type!r}. Allowed: {', '.join(GROWTH_TYPES)}."
        )

    if not ward or not ward.strip():
        raise ComputeGrowthError("ward must be a non-empty string.")
    if not category or not category.strip():
        raise ComputeGrowthError("category must be a non-empty string.")

    nw, nc = _norm_label(ward), _norm_label(category)
    scoped = [
        r
        for r in rows
        if _norm_label(str(r.get("ward", ""))) == nw
        and _norm_label(str(r.get("category", ""))) == nc
    ]
    scoped.sort(key=lambda r: r["period"])

    if not scoped:
        raise ComputeGrowthError(
            f"No rows for ward={ward!r} and category={category!r}."
        )

    canonical_ward = str(scoped[0]["ward"])
    canonical_category = str(scoped[0]["category"])

    by_period: dict[str, dict[str, Any]] = {r["period"]: r for r in scoped}
    out: list[dict[str, Any]] = []

    for rec in scoped:
        period = rec["period"]
        spend = rec["actual_spend"]
        notes = rec.get("notes") or ""

        base: dict[str, Any] = {
            "period": period,
            "ward": canonical_ward,
            "category": canonical_category,
            "growth_type": canonical,
            "budgeted_amount": rec["budgeted_amount"],
            "actual_spend": "" if spend is None else spend,
            "notes": notes,
        }

        if spend is None:
            base["growth_pct"] = ""
            base["formula"] = (
                f"FLAGGED: actual_spend is null for {period} — growth not computed; "
                f"notes: {notes}"
            )
            out.append(base)
            continue

        if canonical == "MoM":
            prev_p = _prev_month(period)
            prev_rec = by_period.get(prev_p) if prev_p else None
            if prev_p is None or prev_rec is None:
                base["growth_pct"] = ""
                base["formula"] = (
                    f"MoM: no prior month in series for {period} — growth not defined."
                )
                out.append(base)
                continue

            prev_spend = prev_rec["actual_spend"]
            if prev_spend is None:
                base["growth_pct"] = ""
                base["formula"] = (
                    f"MoM: prior month {prev_p} has null actual_spend — not computed; "
                    f"notes: {prev_rec.get('notes') or ''}"
                )
                out.append(base)
                continue

            if prev_spend == 0:
                base["growth_pct"] = ""
                base["formula"] = (
                    f"MoM: prior month actual_spend is 0 — ratio undefined."
                )
                out.append(base)
                continue

            pct = (spend - prev_spend) / prev_spend * 100.0
            base["growth_pct"] = round(pct, 1)
            base["formula"] = (
                f"MoM: ((actual_spend[{period}] - actual_spend[{prev_p}]) / actual_spend[{prev_p}]) × 100 "
                f"= (({spend} - {prev_spend}) / {prev_spend}) × 100 = {_format_pct(pct)}"
            )
            out.append(base)
            continue

        # YoY
        yoy_p = _prev_year_month(period)
        yoy_rec = by_period.get(yoy_p)
        if yoy_rec is None:
            base["growth_pct"] = ""
            base["formula"] = (
                f"YoY: period {yoy_p} not in dataset — cannot compute year-over-year for {period}."
            )
            out.append(base)
            continue

        yoy_spend = yoy_rec["actual_spend"]
        if yoy_spend is None:
            base["growth_pct"] = ""
            base["formula"] = (
                f"YoY: {yoy_p} has null actual_spend — not computed; "
                f"notes: {yoy_rec.get('notes') or ''}"
            )
            out.append(base)
            continue

        if yoy_spend == 0:
            base["growth_pct"] = ""
            base["formula"] = (
                f"YoY: prior-year actual_spend for {yoy_p} is 0 — ratio undefined."
            )
            out.append(base)
            continue

        pct = (spend - yoy_spend) / yoy_spend * 100.0
        base["growth_pct"] = round(pct, 1)
        base["formula"] = (
            f"YoY: ((actual_spend[{period}] - actual_spend[{yoy_p}]) / actual_spend[{yoy_p}]) × 100 "
            f"= (({spend} - {yoy_spend}) / {yoy_spend}) × 100 = {_format_pct(pct)}"
        )
        out.append(base)

    return out


def _emit_null_report(null_rows: list[NullRowReport], file: Any = sys.stderr) -> None:
    print(
        f"[load_dataset] Null actual_spend rows in dataset (count={len(null_rows)}):",
        file=file,
    )
    for nr in null_rows:
        print(
            f"  {nr.period} | {nr.ward} | {nr.category} | notes: {nr.notes or '(empty)'}",
            file=file,
        )


def write_output_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="UC-0C ward/category budget growth.")
    p.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )
    p.add_argument(
        "--output",
        required=True,
        help="Output CSV path (e.g. growth_output.csv)",
    )
    p.add_argument("--ward", required=True, help="Single ward name (exact string).")
    p.add_argument(
        "--category",
        required=True,
        help="Single category name (exact string).",
    )
    p.add_argument(
        "--growth-type",
        required=True,
        dest="growth_type",
        metavar="TYPE",
        help="Growth measure: MoM or YoY (required — not guessed).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        loaded = load_dataset(args.input)
    except LoadDatasetError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    _emit_null_report(loaded.null_rows)

    try:
        result_rows = compute_growth(
            loaded.rows,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ComputeGrowthError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    write_output_csv(out_path, result_rows)
    print(f"Wrote {len(result_rows)} row(s) to {out_path.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
