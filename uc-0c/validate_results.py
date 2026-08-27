"""Validate growth_output.csv against every agents.md enforcement rule.

Usage:
    python validate_results.py                        # defaults to growth_output.csv
    python validate_results.py path/to/output.csv

Enforcement rules checked:
  1. Never aggregate — every row must have a specific ward and category (not blank/All).
  2. Null rows must be flagged — actual_spend containing NULL must have NOT COMPUTED
     in growth_pct, never a numeric value.
  3. Formula must be shown — formula field must be non-empty on every row.
  4. Reference values — spot-check pinned values from the README.
  5. Required output columns must all be present.
"""

import csv
import sys

REQUIRED_COLUMNS = {
    "period", "ward", "category",
    "actual_spend", "prior_period", "prior_period_spend",
    "formula", "growth_pct",
}

# Reference values from README — (ward, category, period) -> expected_growth_pct
REFERENCE_VALUES = {
    ("Ward 1 \u2013 Kasba", "Roads & Pothole Repair", "2024-07"): 33.1,
    ("Ward 1 \u2013 Kasba", "Roads & Pothole Repair", "2024-10"): -34.8,
}

# Rows that must be flagged NULL — (ward, category, period)
KNOWN_NULL_ROWS = {
    ("Ward 2 \u2013 Shivajinagar", "Drainage & Flooding",       "2024-03"),
    ("Ward 4 \u2013 Warje",        "Roads & Pothole Repair",    "2024-07"),
    ("Ward 1 \u2013 Kasba",        "Waste Management",          "2024-11"),
    ("Ward 3 \u2013 Kothrud",      "Parks & Greening",          "2024-08"),
    ("Ward 5 \u2013 Hadapsar",     "Streetlight Maintenance",   "2024-05"),
}

results_file = sys.argv[1] if len(sys.argv) > 1 else "growth_output.csv"

try:
    with open(results_file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            sys.exit(f"ERROR: '{results_file}' is empty or unreadable.")
        rows = list(reader)
except FileNotFoundError:
    sys.exit(f"ERROR: File not found: '{results_file}'")

errors = []

# ── Rule 5: required columns present ─────────────────────────────────────────
present = {c.strip() for c in (rows[0].keys() if rows else [])}
missing_cols = REQUIRED_COLUMNS - present
if missing_cols:
    errors.append(f"MISSING COLUMNS: {', '.join(sorted(missing_cols))}")

# ── Per-row checks ────────────────────────────────────────────────────────────
seen_null_keys = set()

for r in rows:
    loc = f"period={r.get('period','?')} ward={r.get('ward','?')} category={r.get('category','?')}"
    ward     = r.get("ward", "").strip()
    category = r.get("category", "").strip()
    period   = r.get("period", "").strip()
    actual   = r.get("actual_spend", "").strip()
    formula  = r.get("formula", "").strip()
    growth   = r.get("growth_pct", "").strip()

    # Rule 1 — no aggregation: ward and category must be specific, non-blank values
    if not ward:
        errors.append(f"{loc}: AGGREGATION VIOLATION — ward is blank")
    if not category:
        errors.append(f"{loc}: AGGREGATION VIOLATION — category is blank")
    if ward.lower() in ("all", "any", "total"):
        errors.append(f"{loc}: AGGREGATION VIOLATION — ward='{ward}' is a cross-ward aggregate")
    if category.lower() in ("all", "any", "total"):
        errors.append(f"{loc}: AGGREGATION VIOLATION — category='{category}' is a cross-category aggregate")

    # Rule 3 — formula must be present on every row
    if not formula:
        errors.append(f"{loc}: MISSING FORMULA — formula field is empty")

    # Rule 2 — null rows must have NOT COMPUTED in growth_pct, never a bare number
    if "NULL" in actual:
        try:
            float(growth)
            # If we reach here, growth parsed as a number — violation
            errors.append(
                f"{loc}: NULL NOT FLAGGED — actual_spend is NULL but growth_pct is numeric: {growth}"
            )
        except ValueError:
            pass  # correctly flagged as non-numeric
        if "NOT COMPUTED" not in growth:
            errors.append(
                f"{loc}: NULL ROW INCOMPLETE — growth_pct should contain 'NOT COMPUTED', got: '{growth}'"
            )
        key = (ward, category, period)
        seen_null_keys.add(key)

# ── Rule 2 (continued) — known null rows must appear and be flagged ───────────
# Only check against the output for the ward/category combination present in the file
output_ward_cats = {(r.get("ward","").strip(), r.get("category","").strip()) for r in rows}
relevant_null_rows = {k for k in KNOWN_NULL_ROWS if (k[0], k[1]) in output_ward_cats}

for key in relevant_null_rows:
    if key not in seen_null_keys:
        errors.append(
            f"NULL ROW NOT FLAGGED — ({key[2]} · {key[0]} · {key[1]}) "
            f"should appear as NULL but was not found or not flagged"
        )

# ── Rule 4 — reference value spot-checks ─────────────────────────────────────
row_index = {
    (r.get("ward","").strip(), r.get("category","").strip(), r.get("period","").strip()): r
    for r in rows
}
for (ward_ref, cat_ref, period_ref), expected in REFERENCE_VALUES.items():
    key = (ward_ref, cat_ref, period_ref)
    if key not in row_index:
        # Only flag if this ward+category was in the output
        if (ward_ref, cat_ref) in output_ward_cats:
            errors.append(
                f"REFERENCE VALUE MISSING — no row for {period_ref} · {ward_ref} · {cat_ref}"
            )
        continue
    row = row_index[key]
    growth_val = row.get("growth_pct", "").strip()
    try:
        actual_val = round(float(growth_val), 1)
        if actual_val != expected:
            errors.append(
                f"REFERENCE VALUE MISMATCH — {period_ref} · {ward_ref} · {cat_ref}: "
                f"expected {expected:+.1f}%, got {actual_val:+.1f}%"
            )
    except ValueError:
        # growth_pct is non-numeric (e.g. NOT COMPUTED) — only an error if we expected a number
        errors.append(
            f"REFERENCE VALUE NOT COMPUTED — {period_ref} · {ward_ref} · {cat_ref}: "
            f"expected {expected:+.1f}%, got '{growth_val}'"
        )

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"Rows validated: {len(rows)}")
print(f"File:           {results_file}")
if errors:
    print(f"\nFAILURES ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print(f"ALL ENFORCEMENT CHECKS PASSED — {len(rows)}/{len(rows)} rows valid")
