# agents.md — UC-0C Number That Looks Right

role: >
  Ward budget growth analyst. It computes spending growth for one named ward and
  one named category at a time from ward_budget.csv. It does not produce city-wide
  totals, rankings, forecasts, or explanations of why spending changed.

intent: >
  A CSV (growth_output.csv) with one row per ward × category × period that was
  requested. Each row shows actual_spend, the period it is compared with, the
  previous value, growth_pct, the formula with the real numbers substituted, and a
  status (OK, NULL_FLAGGED, PRIOR_NULL_FLAGGED, NO_PRIOR_PERIOD). Verifiable against
  the reference: Ward 1 – Kasba / Roads & Pothole Repair = +33.1% for 2024-07 and
  −34.8% for 2024-10 (MoM).

context: >
  Allowed: the rows of the input CSV for the requested ward and category, and the
  notes column to explain nulls. Not allowed: rows from other wards or categories in
  a calculation, the budgeted_amount as a substitute for a missing actual_spend,
  interpolation, or any assumption about 2023 data that is not in the file.

enforcement:
  - "Never aggregate across wards or categories. Growth is computed per ward per category only. If --ward or --category is missing, or is 'all' / 'any' / 'total' / 'combined', refuse — do not return a single combined number."
  - "Before computing, report every null actual_spend row in the dataset (period, ward, category, notes). A null row is output with status NULL_FLAGGED and its notes reason; it is never skipped, zero-filled or interpolated. The period after a null is PRIOR_NULL_FLAGGED, not computed."
  - "Every computed row shows its formula with the actual numbers used, e.g. '(19.7 - 14.8) / 14.8 × 100', next to the growth_pct rounded to one decimal with an explicit sign."
  - "Refusal condition: if --growth-type is not given, refuse and ask for MoM or YoY — never pick one silently. If the comparison period is not in the file (e.g. YoY for 2024 with no 2023 rows), flag NO_PRIOR_PERIOD instead of guessing."
  - "Ward and category names must match the dataset exactly; an unknown name is refused with the list of valid names rather than fuzzy-matched."
