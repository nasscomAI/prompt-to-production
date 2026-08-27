"""
UC-0C app.py — Number That Looks Right.

Computes per-ward, per-category spend growth (MoM or YoY) from the civic
budget CSV. Defeats the three named failure modes of this UC:

  * Silent aggregation across wards/categories  -> REFUSE (exit 3, no output)
  * Silent null skipping                        -> FLAG every null row before compute
  * Silent formula assumption (MoM vs YoY)      -> REFUSE if --growth-type invalid/omitted

Pure standard-library Python 3.9. No network, no third-party packages, no
LLM/API at runtime. Deterministic and rule-based.

Run (from repo root):
    python uc-0c/app.py --input data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
        --growth-type MoM --output uc-0c/growth_output.csv
"""
import argparse
import csv
import sys
from pathlib import Path

# Resolve every default path from THIS file's location, so the same command
# works whether it is launched from the repo root (python uc-0c/app.py ...)
# or from inside the uc-0c folder (python app.py ...).
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_INPUT = REPO_ROOT / "data" / "budget" / "ward_budget.csv"
DEFAULT_OUTPUT = SCRIPT_DIR / "growth_output.csv"

REQUIRED_COLUMNS = [
    "period", "ward", "category",
    "budgeted_amount", "actual_spend", "notes",
]
VALID_GROWTH_TYPES = {"MoM", "YoY"}
OUTPUT_COLUMNS = [
    "period", "ward", "category",
    "actual_spend", "growth_pct", "formula", "note",
]

# Tokens that mean "aggregate everything" and must be refused. Lowercased.
AGGREGATE_TOKENS = {
    "", "all", "*", "every", "total", "any", "overall",
    "all wards", "all categories", "all ward", "all category",
}

# Exit codes.
EXIT_BAD_INPUT = 2
EXIT_REFUSED = 3


# --------------------------------------------------------------------------- #
# Refusal helper — the RICE "REFUSE and ask, never guess" rule.
# --------------------------------------------------------------------------- #
def refuse(message):
    """Print a clear refusal to stderr and exit non-zero without writing output."""
    print("REFUSED: " + message, file=sys.stderr)
    sys.exit(EXIT_REFUSED)


def _is_aggregate_token(value):
    """True when a ward/category argument means 'aggregate everything'."""
    if value is None:
        return True
    return value.strip().lower() in AGGREGATE_TOKENS


def _num(x):
    """Shortest clean decimal rendering of a float parsed from the CSV.

    str(float) in Python 3 already round-trips to the shortest form, so
    19.7 renders as '19.7' (not 19.700000001). This wrapper keeps the formula
    string readable and deterministic.
    """
    if float(x).is_integer():
        return str(int(x))
    return repr(float(x))


# --------------------------------------------------------------------------- #
# Skill: load_dataset
# --------------------------------------------------------------------------- #
def load_dataset(input_path):
    """Read the CSV, validate required columns, collect NULL actual_spend rows.

    Prints a null report to stdout BEFORE returning, so nulls are surfaced
    before any computation happens (defeats silent null skipping).

    Returns (rows, null_rows, wards, categories):
      * rows         — list of dict rows (full dataset)
      * null_rows    — list of {period, ward, category, notes} for blank actual_spend
      * wards        — sorted list of distinct ward strings present in the data
      * categories   — sorted list of distinct category strings present in the data
    """
    path = Path(input_path)
    if not path.exists():
        print(f"ERROR: input file not found: {path}", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            print(
                "ERROR: input CSV is missing required column(s): "
                + ", ".join(missing),
                file=sys.stderr,
            )
            sys.exit(EXIT_BAD_INPUT)
        rows = list(reader)

    # Collect null rows and the distinct ward/category universes.
    null_rows = []
    wards = set()
    categories = set()
    for r in rows:
        wards.add(r["ward"])
        categories.add(r["category"])
        spend = (r.get("actual_spend") or "").strip()
        if spend == "":
            null_rows.append({
                "period": r["period"],
                "ward": r["ward"],
                "category": r["category"],
                "notes": (r.get("notes") or "").strip(),
            })

    # Null report — printed to stdout before any growth math runs.
    print(
        f"Dataset loaded: {len(rows)} rows across {len(wards)} ward(s) and "
        f"{len(categories)} category/categories. "
        f"{len(null_rows)} NULL actual_spend row(s) found."
    )
    if null_rows:
        print("NULL actual_spend rows (FLAGGED — not silently skipped):")
        for nr in null_rows:
            reason = nr["notes"] if nr["notes"] else "no reason recorded"
            print(
                f"  - period={nr['period']} | ward={nr['ward']} | "
                f"category={nr['category']} | reason: {reason}"
            )

    return rows, null_rows, sorted(wards), sorted(categories)


# --------------------------------------------------------------------------- #
# Skill: compute_growth
# --------------------------------------------------------------------------- #
def compute_growth(rows, ward, category, growth_type):
    """Filter to ONE ward + ONE category, sort by period, compute per-period growth.

    Returns a list of result dicts (one row per period) with keys:
      period, ward, category, actual_spend, growth_pct, formula, note

    Rules enforced here:
      * Null actual_spend row      -> growth_pct/formula blank,
                                      note = 'NULL — <reason from notes>'.
      * MoM, first period          -> growth blank, note = 'no prior period'.
      * MoM, prior period is NULL  -> growth blank, note flags the chained null.
      * YoY (dataset is 2024 only) -> growth blank on every row,
                                      note = 'YoY N/A — dataset spans only 2024'.
    """
    matched = [r for r in rows if r["ward"] == ward and r["category"] == category]
    matched.sort(key=lambda r: r["period"])

    results = []
    for i, r in enumerate(matched):
        period = r["period"]
        spend_raw = (r.get("actual_spend") or "").strip()
        note_src = (r.get("notes") or "").strip()

        # --- NULL row: flag, never compute, never skip ---------------------
        if spend_raw == "":
            reason = note_src if note_src else "no reason recorded"
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": "", "growth_pct": "", "formula": "",
                "note": f"NULL — {reason}",
            })
            continue

        actual = float(spend_raw)

        if growth_type == "MoM":
            if i == 0:
                results.append({
                    "period": period, "ward": ward, "category": category,
                    "actual_spend": spend_raw, "growth_pct": "", "formula": "",
                    "note": "no prior period",
                })
                continue

            prev = matched[i - 1]
            prev_raw = (prev.get("actual_spend") or "").strip()
            if prev_raw == "":
                # Prior period was NULL — cannot divide. Chain the flag.
                results.append({
                    "period": period, "ward": ward, "category": category,
                    "actual_spend": spend_raw, "growth_pct": "", "formula": "",
                    "note": "prior period actual_spend is NULL — growth not computed",
                })
                continue

            prev_val = float(prev_raw)
            growth = (actual - prev_val) / prev_val * 100.0
            formula = f"({_num(actual)}-{_num(prev_val)})/{_num(prev_val)}*100"
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": spend_raw,
                "growth_pct": f"{growth:.1f}",
                "formula": formula,
                "note": "",
            })

        else:  # growth_type == "YoY"
            # Dataset spans only 2024, so same-month-prior-year does not exist.
            results.append({
                "period": period, "ward": ward, "category": category,
                "actual_spend": spend_raw, "growth_pct": "", "formula": "",
                "note": "YoY N/A — dataset spans only 2024 (no prior year)",
            })

    return results


# --------------------------------------------------------------------------- #
# Output writer
# --------------------------------------------------------------------------- #
def write_output(output_path, results):
    out = Path(output_path)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"Wrote {len(results)} row(s) to {out}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="app.py",
        description=(
            "UC-0C: compute per-ward, per-category spend growth (MoM or YoY). "
            "Refuses all-ward/all-category aggregation and unknown growth types."
        ),
    )
    p.add_argument(
        "--input", default=str(DEFAULT_INPUT),
        help="Path to ward_budget.csv (default: data/budget/ward_budget.csv "
             "resolved from this script's location).",
    )
    p.add_argument(
        "--ward", default=None,
        help="Exactly ONE ward, e.g. 'Ward 1 – Kasba' (en dash U+2013). "
             "Missing/'all'/wildcard -> refused.",
    )
    p.add_argument(
        "--category", default=None,
        help="Exactly ONE category, e.g. 'Roads & Pothole Repair'. "
             "Missing/'all'/wildcard -> refused.",
    )
    p.add_argument(
        "--growth-type", dest="growth_type", default=None,
        help="Required: 'MoM' or 'YoY' (case-sensitive). Anything else -> refused.",
    )
    p.add_argument(
        "--output", default=str(DEFAULT_OUTPUT),
        help="Output CSV path (default: growth_output.csv next to this script).",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # --- Enforcement 4: growth-type must be explicit, never guessed ---------
    if args.growth_type is None or args.growth_type not in VALID_GROWTH_TYPES:
        got = repr(args.growth_type) if args.growth_type is not None else "<omitted>"
        refuse(
            f"--growth-type must be exactly one of {sorted(VALID_GROWTH_TYPES)} "
            f"(got {got}). The system never guesses the growth formula. "
            f"Re-run with --growth-type MoM or --growth-type YoY."
        )

    # --- Enforcement 1: refuse all-ward / all-category aggregation ----------
    if _is_aggregate_token(args.ward):
        got = repr(args.ward) if args.ward is not None else "<omitted>"
        refuse(
            f"--ward must name exactly ONE ward (got {got}). "
            f"Aggregating or averaging across wards is not allowed. "
            f"Pass a single ward such as 'Ward 1 – Kasba'."
        )
    if _is_aggregate_token(args.category):
        got = repr(args.category) if args.category is not None else "<omitted>"
        refuse(
            f"--category must name exactly ONE category (got {got}). "
            f"Aggregating or averaging across categories is not allowed. "
            f"Pass a single category such as 'Roads & Pothole Repair'."
        )

    # --- Load + null report -------------------------------------------------
    rows, null_rows, wards, categories = load_dataset(args.input)

    # --- Enforcement 6: ward/category must exist (byte-exact, incl. en dash) -
    if args.ward not in wards:
        refuse(
            f"--ward {args.ward!r} matches no row in the dataset. "
            f"Valid wards: {wards}. Note: ward names use an en dash (U+2013), "
            f"e.g. 'Ward 1 – Kasba' — match byte-for-byte, do not normalise."
        )
    if args.category not in categories:
        refuse(
            f"--category {args.category!r} matches no row in the dataset. "
            f"Valid categories: {categories}."
        )

    # --- Compute + write ----------------------------------------------------
    results = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, results)


if __name__ == "__main__":
    main()
