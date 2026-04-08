"""
app.py — UC-0C BudgetGrowthAgent
Built from: agents.md (RICE enforcement rules) + skills.md (skill contracts)

Usage:
    python app.py \
        --input  ../data/budget/ward_budget.csv \
        --ward   "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv

Enforcement rules (agents.md, P0 first):
    P0-1  Never aggregate across wards or categories — REFUSE if asked
    P0-2  Flag every null row before computing — report reason from notes
    P1-3  Show formula_used in every output row — never empty
    P1-4  Refuse if --growth-type not specified — never guess
    P2-5  Validate required columns on load — fail fast
"""

import argparse
import csv
import sys
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
}

VALID_GROWTH_TYPES   = {"MoM", "YoY", "QoQ"}
GROWTH_TYPE_CANONICAL = {g.upper(): g for g in VALID_GROWTH_TYPES}

GROWTH_TYPE_LABELS = {
    "MoM": "Month-over-Month",
    "YoY": "Year-over-Year",
    "QoQ": "Quarter-over-Quarter",
}

GROWTH_TYPE_OFFSETS = {
    "MoM": 1,
    "YoY": 12,
    "QoQ": 3,
}

# agents.md Rule 1 — aggregation alias list
AGGREGATION_ALIASES = {"all", "all wards", "all categories", "*", "total", "aggregate", "any"}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: load_dataset
# Source: skills.md §load_dataset
#   input:  filepath: str
#   output: list[dict]  — nulls preserved as "", null audit printed before return
#   error_handling:
#     File not found       → [ERROR] … exit 1
#     Empty CSV            → [ERROR] … exit 1
#     Missing columns      → [ERROR] … exit 1
#     notes blank on null  → "Reason: not recorded" — do not error
#   contract:
#     Null audit runs unconditionally — cannot be skipped
#     Null rows returned unchanged (actual_spend = "")
#     No fill / drop / impute
# ─────────────────────────────────────────────────────────────────────────────

def load_dataset(filepath: str) -> list:
    path = Path(filepath)

    # error_handling: file not found
    if not path.exists():
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # error_handling: empty CSV
    if not rows:
        print("[ERROR] CSV is empty.")
        sys.exit(1)

    # P2-5 (agents.md) — validate required columns
    present = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - present
    if missing:
        print(f"[ERROR] Missing required columns: {sorted(missing)}")
        sys.exit(1)

    # contract: null audit runs unconditionally before returning data
    null_rows = [r for r in rows if r.get("actual_spend", "").strip() == ""]
    _print_null_audit(filepath, len(rows), null_rows)

    return rows  # contract: unchanged — nulls preserved as ""


def _print_null_audit(filepath, total, null_rows):
    """agents.md Rule 2 (P0) — print null report before any computation."""
    print(f"\n{'─' * 62}")
    print(f"  DATASET LOADED    : {filepath}")
    print(f"  Total rows        : {total}")
    print(f"  Null actual_spend : {len(null_rows)}")
    if null_rows:
        print(f"\n  WARNING  NULL ROWS (will be flagged, not computed):")
        for r in null_rows:
            reason = r.get("notes", "").strip() or "not recorded"
            print(f"     * {r['period']} | {r['ward']} | {r['category']}")
            print(f"       Reason: {reason}")
    print(f"{'─' * 62}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Skill: compute_growth
# Source: skills.md §compute_growth
#   input:  rows, ward, category, growth_type
#   output: list[dict] — one per period, sorted, formula_used never empty
#   contract:
#     Filters to exactly one (ward, category) pair
#     Null rows appear in output — never dropped/skipped/zero-filled
#     formula_used populated on every row without exception
#     Offsets: MoM=1, QoQ=3, YoY=12
# ─────────────────────────────────────────────────────────────────────────────

def compute_growth(rows, ward, category, growth_type):

    # skills.md error_handling: growth_type empty
    if not growth_type or not growth_type.strip():
        print("[REFUSED] --growth-type is required and was not provided.")
        print("          Please specify one of: MoM, YoY, QoQ")
        print("          This tool never guesses a growth type.")
        sys.exit(1)

    # skills.md error_handling: growth_type not in valid set
    canonical = GROWTH_TYPE_CANONICAL.get(growth_type.strip().upper())
    if canonical is None:
        print(f"[ERROR] Unknown --growth-type '{growth_type}'.")
        print(f"        Valid options: MoM, YoY, QoQ")
        sys.exit(1)
    growth_type = canonical

    # agents.md Rule 1 (P0) — refuse aggregation aliases
    if ward.lower().strip() in AGGREGATION_ALIASES or \
       category.lower().strip() in AGGREGATION_ALIASES:
        print("[REFUSED] Aggregation across wards or categories is not permitted.")
        print("          You must specify an exact --ward and --category.")
        print("          This system produces per-ward, per-category outputs only.")
        sys.exit(1)

    # skills.md contract: filter to exactly one (ward, category) pair
    subset = [
        r for r in rows
        if r["ward"].strip() == ward.strip()
        and r["category"].strip() == category.strip()
    ]

    # skills.md error_handling: no rows match filter
    if not subset:
        print(f"[ERROR] No data found for ward='{ward}' / category='{category}'.")
        print("        Check spelling. Valid values in this dataset:")
        print(f"  Wards      : {sorted({r['ward'] for r in rows})}")
        print(f"  Categories : {sorted({r['category'] for r in rows})}")
        sys.exit(1)

    subset.sort(key=lambda r: r["period"])

    # Build period → value lookup; None = null (skills.md contract: no zero-fill)
    period_map = {}
    for r in subset:
        raw = r.get("actual_spend", "").strip()
        period_map[r["period"]] = float(raw) if raw != "" else None

    periods = sorted(period_map.keys())
    offset  = GROWTH_TYPE_OFFSETS[growth_type]
    label   = GROWTH_TYPE_LABELS[growth_type]

    results = []
    for i, period in enumerate(periods):
        current_val = period_map[period]

        # Resolve comparison period by growth_type
        if growth_type == "MoM":
            prev_period = periods[i - offset] if i >= offset else None
        else:
            candidate = _add_months(period, -offset)
            prev_period = candidate if candidate in period_map else None

        prev_val = period_map.get(prev_period) if prev_period else None

        # ── skills.md: status + formula_used matrix (agents.md Rule 3) ───────
        null_reason = ""
        if current_val is None:
            # agents.md Rule 2: null row must appear; status + formula set
            null_reason  = _get_null_reason(subset, period)
            status       = "NULL \u2014 not computed"
            growth_str   = ""
            formula_used = "N/A (null actual_spend)"

        elif prev_period is None:
            status       = "No prior period \u2014 growth undefined"
            growth_str   = ""
            formula_used = "N/A (no prior period in dataset)"

        elif prev_val is None:
            status       = f"Prior period ({prev_period}) is NULL \u2014 growth undefined"
            growth_str   = ""
            formula_used = "N/A (prior period is null)"

        elif prev_val == 0.0:
            status       = "Prior period is 0 \u2014 division undefined"
            growth_str   = ""
            formula_used = "N/A (division by zero)"

        else:
            # agents.md Rule 3 (P1): formula shown in every output row
            # skills.md formula format: (<current> − <prev>) / <prev> × 100 = <r>%
            pct          = (current_val - prev_val) / prev_val * 100
            status       = "OK"
            growth_str   = f"{pct:+.1f}%"
            formula_used = (
                f"({current_val} \u2212 {prev_val}) / {prev_val} \u00d7 100"
                f" = {pct:+.1f}%"
            )

        # skills.md output schema
        results.append({
            "period":               period,
            "ward":                 ward,
            "category":             category,
            "actual_spend":         current_val if current_val is not None else "NULL",
            "prev_period":          prev_period or "\u2014",
            "prev_actual_spend":    (
                prev_val if prev_val is not None
                else ("NULL" if prev_period else "\u2014")
            ),
            f"{growth_type}_growth": growth_str,
            "status":               status,
            "null_reason":          null_reason,
            "formula_used":         formula_used,   # contract: never empty
            "growth_type":          label,
        })

    return results


def _get_null_reason(subset, period):
    for r in subset:
        if r["period"] == period:
            return r.get("notes", "").strip() or "not recorded"
    return "not recorded"


def _add_months(period, months):
    year, month = int(period[:4]), int(period[5:7])
    total = year * 12 + (month - 1) + months
    y, m  = divmod(total, 12)
    return f"{y}-{m + 1:02d}"


# ── Output ────────────────────────────────────────────────────────────────────

def write_output(results, output_path, growth_type):
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    growth_col = f"{growth_type}_growth"
    fieldnames = [
        "period", "ward", "category",
        "actual_spend", "prev_period", "prev_actual_spend",
        growth_col, "status", "null_reason", "formula_used", "growth_type",
    ]

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"[OUTPUT] {out.resolve()}  ({len(results)} rows)\n")
    _print_summary(results, growth_col)


def _print_summary(results, growth_col):
    W = [8, 7, 7, 10, 36, 36]
    hdrs = ["period", "actual", "prev", "growth", "status", "formula_used"]
    sep  = "  ".join("─" * w for w in W)

    def fmt(vals):
        return "  ".join(str(v)[:w].ljust(w) for v, w in zip(vals, W))

    print(f"  {fmt(hdrs)}")
    print(f"  {sep}")
    for r in results:
        print("  " + fmt([
            r["period"],
            str(r["actual_spend"]),
            str(r["prev_actual_spend"]),
            str(r.get(growth_col, "")),
            r["status"],
            r["formula_used"],
        ]))
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        prog="app.py",
        description="UC-0C BudgetGrowthAgent — per-ward, per-category spending growth.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--input",       required=True,  metavar="CSV")
    p.add_argument("--ward",        required=True,  metavar="WARD")
    p.add_argument("--category",    required=True,  metavar="CATEGORY")
    p.add_argument("--growth-type", dest="growth_type", default="", metavar="TYPE",
                   help="MoM | YoY | QoQ  — REQUIRED, never defaulted")
    p.add_argument("--output",      required=True,  metavar="OUT")
    return p


def main():
    args = build_parser().parse_args()

    # agents.md Rule 4 (P1): refuse at CLI boundary before any skill runs
    if not args.growth_type or not args.growth_type.strip():
        print("[REFUSED] --growth-type is required and was not provided.")
        print("          Please specify one of: MoM, YoY, QoQ")
        print("          This tool never guesses a growth type.")
        sys.exit(1)

    # agents.md Rule 1 (P0): refuse aggregation aliases at CLI boundary
    if args.ward.lower().strip() in AGGREGATION_ALIASES or \
       args.category.lower().strip() in AGGREGATION_ALIASES:
        print("[REFUSED] Aggregation across wards or categories is not permitted.")
        print("          You must specify an exact --ward and --category.")
        print("          This system produces per-ward, per-category outputs only.")
        sys.exit(1)

    rows    = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    gt      = GROWTH_TYPE_CANONICAL.get(args.growth_type.strip().upper(), args.growth_type.upper())
    write_output(results, args.output, gt)


if __name__ == "__main__":
    main()