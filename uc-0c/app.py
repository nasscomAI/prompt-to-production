"""
UC-0C — Municipal Ward Infrastructure Budget and Growth Analytics

Implements the RICE specification defined in agents.md and skills.md:
  - Skill 1: load_dataset  — reads CSV, validates schema, reports all null rows
                             verbatim from notes before returning.
  - Skill 2: compute_growth — filters by ward + category + growth_type,
                              produces a per-period table with:
                                * actual_spend
                                * budgeted_amount
                                * growth_pct (formatted or NULL)
                                * formula (exact mathematical expression)
                                * null_flag + null_reason (verbatim from notes)

Enforcement (from agents.md):
  * No aggregation: --ward and --category are mandatory; refusal if omitted or
    requested to be applied across all wards / all categories.
  * Null transparency: every null actual_spend is flagged before computation;
    growth is marked NULL / uncomputable — never zero-filled or silently dropped.
  * Formula visibility: each output row carries the exact formula string used.
  * Growth-type refusal: --growth-type is mandatory; execution refused if missing
    or invalid — never guessed.
  * File refusal: execution refused immediately on missing / empty file or
    missing required columns.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS: Tuple[str, ...] = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)

SUPPORTED_GROWTH_TYPES: Tuple[str, ...] = ("MoM", "YoY")

OUTPUT_COLUMNS: Tuple[str, ...] = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "growth_type",
    "growth_pct",
    "formula",
    "null_flag",
    "null_reason",
)

# Formula string templates — shown verbatim in every output row.
FORMULA_BASE = "Initial Period (Base) — no prior period to compare"
FORMULA_MOM = "((actual_spend_t - actual_spend_t-1) / actual_spend_t-1) * 100"
FORMULA_YOY = "((actual_spend_t - actual_spend_t-12) / actual_spend_t-12) * 100"
FORMULA_NULL_CURRENT = "Null Spend in Current Period — growth uncomputable"
FORMULA_NULL_PRIOR = "Null Spend in Prior Period — growth uncomputable"
FORMULA_NO_PRIOR = "No Prior Period in Dataset — growth uncomputable"

NULL_FLAG_VALUE = "NULL_SPEND"


# ---------------------------------------------------------------------------
# Skill 1 — load_dataset
# ---------------------------------------------------------------------------

def load_dataset(file_path: str) -> Dict[str, Any]:
    """
    Skill: load_dataset
    Reads a municipal ward budget CSV file, validates required schema, scans
    for missing actual_spend values, and reports every null row verbatim from
    the notes column before returning.

    Args:
        file_path: Path to the input CSV (must include columns: period, ward,
                   category, budgeted_amount, actual_spend, notes).

    Returns:
        Dict with keys:
          'records'      — List[Dict] of all rows with typed actual_spend
                           (float or None) and float budgeted_amount.
          'null_records' — List[Dict] of rows where actual_spend is empty/null.
          'total_rows'   — int, total data rows read.

    Raises:
        FileNotFoundError: If the file path does not exist.
        ValueError:        If the file is empty, unreadable, or missing any
                           required column.
    """
    path = Path(file_path)

    # --- Refusal: file not found ---
    if not path.exists():
        raise FileNotFoundError(
            f"[REFUSAL] Input file not found: '{file_path}'. "
            "Provide a valid path to the ward budget CSV. Execution refused."
        )
    if not path.is_file():
        raise ValueError(
            f"[REFUSAL] Specified path is not a regular file: '{file_path}'. "
            "Execution refused."
        )

    # Read raw text first to detect empty file.
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="latin-1")

    if not raw.strip():
        raise ValueError(
            f"[REFUSAL] Input file '{file_path}' is empty. Execution refused."
        )

    # Parse CSV.
    try:
        lines = raw.splitlines()
        reader = csv.DictReader(lines)
        header = reader.fieldnames or []
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            f"[REFUSAL] Could not parse CSV file '{file_path}': {exc}. "
            "Execution refused."
        ) from exc

    # --- Refusal: missing required columns ---
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing_cols:
        raise ValueError(
            f"[REFUSAL] Input file is missing required column(s): "
            f"{missing_cols}. "
            f"Required columns are: {list(REQUIRED_COLUMNS)}. "
            "Execution refused."
        )

    records: List[Dict[str, Any]] = []
    null_records: List[Dict[str, Any]] = []

    for row_num, row in enumerate(reader, start=2):  # row 1 = header
        spend_raw = row["actual_spend"].strip()
        budget_raw = row["budgeted_amount"].strip()

        # Parse budgeted_amount (always present per spec).
        try:
            budgeted_amount = float(budget_raw)
        except ValueError:
            budgeted_amount = None  # type: ignore[assignment]

        # Parse actual_spend — None when blank.
        if spend_raw == "":
            actual_spend: Optional[float] = None
        else:
            try:
                actual_spend = float(spend_raw)
            except ValueError:
                actual_spend = None

        record: Dict[str, Any] = {
            "period": row["period"].strip(),
            "ward": row["ward"].strip(),
            "category": row["category"].strip(),
            "budgeted_amount": budgeted_amount,
            "actual_spend": actual_spend,
            "notes": row["notes"].strip(),
            "_row_num": row_num,
        }

        records.append(record)

        if actual_spend is None:
            null_records.append(record)

    if not records:
        raise ValueError(
            f"[REFUSAL] Input file '{file_path}' contains no data rows. "
            "Execution refused."
        )

    return {
        "records": records,
        "null_records": null_records,
        "total_rows": len(records),
    }


# ---------------------------------------------------------------------------
# Skill 2 — compute_growth
# ---------------------------------------------------------------------------

def compute_growth(
    records: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, Any]]:
    """
    Skill: compute_growth
    Filters validated budget records by ward and category, then computes
    period-over-period spend growth with explicit formula documentation and
    null flagging.

    MoM (Month-over-Month):
        Compares period t to period t-1 (immediately preceding calendar month).
        Formula: ((actual_spend_t - actual_spend_t-1) / actual_spend_t-1) * 100

    YoY (Year-over-Year):
        Compares period t to period t-12 (same month, prior year).
        Formula: ((actual_spend_t - actual_spend_t-12) / actual_spend_t-12) * 100

    Args:
        records:     Validated budget records from load_dataset.
        ward:        Target ward name (exact match required).
        category:    Target category name (exact match required).
        growth_type: 'MoM' or 'YoY' — anything else causes a refusal.

    Returns:
        List[Dict] with one row per period containing:
          period, ward, category, budgeted_amount, actual_spend,
          growth_type, growth_pct, formula, null_flag, null_reason.

    Raises:
        ValueError: On invalid/missing growth_type, ward/category not in
                    dataset, or wildcard aggregation attempts.
    """

    # --- Refusal: growth_type missing or invalid ---
    if not growth_type or growth_type.strip() == "":
        raise ValueError(
            "[REFUSAL] --growth-type was not specified. "
            "You must explicitly provide 'MoM' (month-over-month) or "
            "'YoY' (year-over-year). Execution refused — never guessed."
        )

    normalized_growth_type = growth_type.strip()
    if normalized_growth_type not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            f"[REFUSAL] Unsupported --growth-type '{growth_type}'. "
            f"Supported values: {SUPPORTED_GROWTH_TYPES}. "
            "Execution refused."
        )

    # --- Refusal: aggregation guard ---
    # Ward or category must be a specific string — not a wildcard.
    AGG_SENTINELS = ("", "*", "all", "ALL", "All")
    if not ward or ward.strip() in AGG_SENTINELS:
        raise ValueError(
            "[REFUSAL] --ward was not specified or set to an aggregation "
            "sentinel value. Cross-ward aggregation is strictly prohibited. "
            "Provide exactly one ward name. Execution refused."
        )
    if not category or category.strip() in AGG_SENTINELS:
        raise ValueError(
            "[REFUSAL] --category was not specified or set to an aggregation "
            "sentinel value. Cross-category aggregation is strictly prohibited. "
            "Provide exactly one category name. Execution refused."
        )

    ward = ward.strip()
    category = category.strip()

    # --- Filter records for this ward + category ---
    filtered = [
        r for r in records
        if r["ward"] == ward and r["category"] == category
    ]

    # --- Refusal: ward or category not found ---
    all_wards = sorted({r["ward"] for r in records})
    all_cats = sorted({r["category"] for r in records})

    if ward not in all_wards:
        raise ValueError(
            f"[REFUSAL] Ward '{ward}' not found in dataset. "
            f"Available wards: {all_wards}. Execution refused."
        )
    if category not in all_cats:
        raise ValueError(
            f"[REFUSAL] Category '{category}' not found in dataset. "
            f"Available categories: {all_cats}. Execution refused."
        )
    if not filtered:
        raise ValueError(
            f"[REFUSAL] No records found for ward='{ward}' and "
            f"category='{category}'. Execution refused."
        )

    # Sort by period (YYYY-MM strings sort lexicographically = chronologically).
    filtered.sort(key=lambda r: r["period"])

    # Build a lookup: period_str -> actual_spend (float or None)
    spend_by_period: Dict[str, Optional[float]] = {
        r["period"]: r["actual_spend"] for r in filtered
    }

    # Build the note lookup for null periods within this ward+category.
    notes_by_period: Dict[str, str] = {
        r["period"]: r["notes"] for r in filtered
    }

    # --- Compute growth for each period ---
    output_rows: List[Dict[str, Any]] = []

    for rec in filtered:
        period = rec["period"]
        actual_spend = rec["actual_spend"]
        budgeted_amount = rec["budgeted_amount"]
        notes = rec["notes"]

        null_flag = ""
        null_reason = ""
        growth_pct_str = ""
        formula_used = ""

        # Step 1: determine prior period key.
        prior_period_key = _prior_period_key(period, normalized_growth_type)
        formula_template = (
            FORMULA_MOM if normalized_growth_type == "MoM" else FORMULA_YOY
        )

        # Step 2: check current period null.
        if actual_spend is None:
            null_flag = NULL_FLAG_VALUE
            null_reason = notes if notes else "No reason recorded"
            growth_pct_str = "NULL"
            formula_used = FORMULA_NULL_CURRENT

        elif prior_period_key is None:
            # No prior period conceptually possible (first YoY period etc.)
            growth_pct_str = "NULL"
            formula_used = FORMULA_NO_PRIOR
            null_reason = f"No comparable prior period for {normalized_growth_type}"

        elif prior_period_key not in spend_by_period:
            # Prior period key is missing from filtered dataset entirely.
            growth_pct_str = "NULL"
            formula_used = FORMULA_BASE if _is_first_period(period, filtered) else FORMULA_NO_PRIOR
            null_reason = (
                "Initial period — no prior period in dataset"
                if _is_first_period(period, filtered)
                else f"Prior period '{prior_period_key}' not found in dataset"
            )

        else:
            prior_spend = spend_by_period[prior_period_key]

            if prior_spend is None:
                # Prior period exists but is null.
                null_flag = NULL_FLAG_VALUE
                null_reason = (
                    f"Prior period ({prior_period_key}) has null spend: "
                    f"{notes_by_period.get(prior_period_key, 'No reason recorded')}"
                )
                growth_pct_str = "NULL"
                formula_used = FORMULA_NULL_PRIOR

            elif prior_spend == 0.0:
                # Guard against division by zero.
                growth_pct_str = "NULL"
                formula_used = formula_template
                null_reason = f"Prior period ({prior_period_key}) actual_spend is 0 — division by zero"

            else:
                # Happy path: compute growth.
                raw_pct = ((actual_spend - prior_spend) / prior_spend) * 100
                # Format to 1 decimal place with leading sign.
                sign = "+" if raw_pct >= 0 else ""
                growth_pct_str = f"{sign}{raw_pct:.1f}%"
                formula_used = formula_template

        output_rows.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": f"{budgeted_amount:.1f}" if budgeted_amount is not None else "",
            "actual_spend": f"{actual_spend:.1f}" if actual_spend is not None else "NULL",
            "growth_type": normalized_growth_type,
            "growth_pct": growth_pct_str,
            "formula": formula_used,
            "null_flag": null_flag,
            "null_reason": null_reason,
        })

    return output_rows


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _prior_period_key(period: str, growth_type: str) -> Optional[str]:
    """Return the ISO YYYY-MM key for the prior comparison period."""
    try:
        year, month = int(period[:4]), int(period[5:7])
    except (ValueError, IndexError):
        return None

    if growth_type == "MoM":
        if month == 1:
            return f"{year - 1:04d}-12"
        return f"{year:04d}-{month - 1:02d}"

    if growth_type == "YoY":
        return f"{year - 1:04d}-{month:02d}"

    return None


def _is_first_period(period: str, filtered: List[Dict[str, Any]]) -> bool:
    """True if period is the earliest in the filtered ward+category set."""
    return filtered and filtered[0]["period"] == period


# ---------------------------------------------------------------------------
# Null report — printed to stderr before computation
# ---------------------------------------------------------------------------

def _print_null_report(null_records: List[Dict[str, Any]]) -> None:
    """
    Prints a preflight null report to stderr before any growth computation.
    Every null actual_spend row is flagged with the verbatim reason from notes.
    """
    if not null_records:
        print("[NULL REPORT] No null actual_spend values found in dataset.", file=sys.stderr)
        return

    print(
        f"\n[NULL REPORT] {len(null_records)} null actual_spend row(s) detected "
        "(growth will be marked NULL / uncomputable for affected periods):",
        file=sys.stderr,
    )
    print("-" * 72, file=sys.stderr)
    for rec in null_records:
        print(
            f"  Period: {rec['period']} | "
            f"Ward: {rec['ward']} | "
            f"Category: {rec['category']} | "
            f"Reason: {rec['notes'] or 'No reason recorded'}",
            file=sys.stderr,
        )
    print("-" * 72, file=sys.stderr)
    print("", file=sys.stderr)


# ---------------------------------------------------------------------------
# CSV output writer
# ---------------------------------------------------------------------------

def _write_output(output_path: str, rows: List[Dict[str, Any]]) -> None:
    """Write computed growth rows to a CSV file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app.py",
        description=(
            "UC-0C — Municipal Ward Infrastructure Budget Growth Analytics.\n"
            "Computes per-ward per-category MoM or YoY expenditure growth "
            "from a budget CSV, with explicit formula documentation and null "
            "flagging."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="FILE",
        help="Path to the input ward budget CSV file.",
    )
    parser.add_argument(
        "--ward",
        required=True,
        metavar="WARD",
        help=(
            'Exact ward name to analyse (e.g. "Ward 1 – Kasba"). '
            "Aggregation across all wards is prohibited."
        ),
    )
    parser.add_argument(
        "--category",
        required=True,
        metavar="CATEGORY",
        help=(
            'Exact category name to analyse (e.g. "Roads & Pothole Repair"). '
            "Aggregation across all categories is prohibited."
        ),
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        metavar="TYPE",
        help=(
            "Growth calculation type: 'MoM' (month-over-month) or "
            "'YoY' (year-over-year). This argument is mandatory — "
            "execution is refused if omitted."
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        metavar="FILE",
        help="Path to write the output CSV (e.g. growth_output.csv).",
    )
    return parser


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Step 1: Skill — load_dataset
    # -----------------------------------------------------------------------
    print(f"[INFO] Loading dataset: {args.input}", file=sys.stderr)
    try:
        dataset = load_dataset(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    total_rows = dataset["total_rows"]
    null_records = dataset["null_records"]
    records = dataset["records"]

    print(
        f"[INFO] Dataset loaded: {total_rows} rows, "
        f"{len(null_records)} null actual_spend value(s).",
        file=sys.stderr,
    )

    # -----------------------------------------------------------------------
    # Step 2: Null preflight report (before any computation)
    # Enforcement: flag every null row verbatim before computing.
    # -----------------------------------------------------------------------
    _print_null_report(null_records)

    # -----------------------------------------------------------------------
    # Step 3: Skill — compute_growth
    # -----------------------------------------------------------------------
    print(
        f"[INFO] Computing {args.growth_type} growth for "
        f"ward='{args.ward}' | category='{args.category}'",
        file=sys.stderr,
    )
    try:
        output_rows = compute_growth(
            records=records,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Step 4: Write output CSV
    # -----------------------------------------------------------------------
    try:
        _write_output(args.output, output_rows)
    except OSError as exc:
        print(f"[ERROR] Could not write output file '{args.output}': {exc}", file=sys.stderr)
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Step 5: Summary to stdout
    # -----------------------------------------------------------------------
    null_in_scope = [
        r for r in output_rows if r["null_flag"] == NULL_FLAG_VALUE
    ]
    computable = [r for r in output_rows if r["growth_pct"] not in ("NULL", "")]
    print(
        f"\n[DONE] Growth output written to: {args.output}\n"
        f"       Periods computed : {len(computable)}\n"
        f"       NULL (uncomputable): {sum(1 for r in output_rows if r['growth_pct'] == 'NULL')}\n"
        f"       Null-flagged rows : {len(null_in_scope)}"
    )

    # Print a quick summary table to stdout for verification.
    print(
        f"\n{'Period':<10}  {'Actual Spend':>13}  {'Budgeted':>10}  "
        f"{'Growth':>9}  Formula"
    )
    print("-" * 80)
    for row in output_rows:
        spend_display = row["actual_spend"] if row["actual_spend"] != "NULL" else "NULL"
        growth_display = row["growth_pct"] if row["growth_pct"] else "—"
        formula_short = row["formula"][:50] + "…" if len(row["formula"]) > 50 else row["formula"]
        print(
            f"{row['period']:<10}  {spend_display:>13}  "
            f"{row['budgeted_amount']:>10}  {growth_display:>9}  {formula_short}"
        )
        if row["null_flag"] == NULL_FLAG_VALUE and row["null_reason"]:
            print(f"           -> [NULL] {row['null_reason']}")
        elif row["null_reason"]:
            print(f"           -> [NOTE] {row['null_reason']}")


if __name__ == "__main__":
    main()
