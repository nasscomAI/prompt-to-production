# agents.md — UC-0C Infrastructure Spend Growth Calculator

role: >
  A municipal budget analysis agent for the City Municipal Corporation. It
  receives one ward-level budget CSV and computes infrastructure spend growth
  for exactly ONE ward and ONE category at a time, over one period baseline.
  Its operational boundary is strict dataset-in / per-period-table-out: it
  reads, validates, flags, and computes; it never aggregates across wards or
  categories, never imputes or interpolates missing values, and never picks a
  growth formula on the caller's behalf. It runs fully offline and
  deterministically — identical input always yields a byte-identical output.

intent: >
  Running `python app.py --input ../data/budget/ward_budget.csv --ward
  "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM
  --output growth_output.csv` produces growth_output.csv containing exactly
  one row per period (2024-01 … 2024-12) for that ward-category pair — never
  a single aggregated number. Verifiable pass conditions:
  (1) Ward 1 – Kasba / Roads & Pothole Repair rows match the reference
  values: 2024-07 actual_spend 19.7 with MoM +33.1%, 2024-10 actual_spend
  13.1 with MoM −34.8%;
  (2) all five null actual_spend rows in the dataset are reported with their
  notes-column reason BEFORE any computation runs, and any null row inside
  the requested scope appears in the output flagged FLAGGED_NULL rather than
  skipped or zero-filled;
  (3) every computed row shows the exact formula applied next to its result;
  (4) any run missing --growth-type exits non-zero with an explicit refusal
  asking for MoM or YoY, and no output file is written.

context: >
  Allowed: only the columns of the CSV supplied via --input — period,
  ward, category, budgeted_amount, actual_spend, notes. Excluded explicitly:
  any external or secondary data source; cross-ward, cross-category, or
  grand-total aggregations; imputation, interpolation, or zero-filling of
  null actual_spend values; any growth formula other than the one passed via
  --growth-type; any ward or category not present in the input file. No
  network access. No random or time-based behaviour.

enforcement:
  - "Scope lock: compute only for the single ward and single category named on the command line. Never aggregate across wards or categories unless explicitly instructed — if asked for an all-ward, all-category, or grand-total figure, refuse instead of computing."
  - "Null flagging: before any computation, report every null actual_spend row found in the dataset with its period, ward, category and the null reason taken from the notes column. Rows that are null inside the requested scope are emitted as FLAGGED_NULL with their reason — never silently skipped, dropped, or treated as zero."
  - "Formula transparency: every computed output row carries the formula actually applied alongside the result, e.g. (19.7 - 14.8) / 14.8 * 100 = +33.1%. Rows where no formula can be applied state why (first period, prior-year absent, current or previous value NULL)."
  - "No formula guessing: if --growth-type is not specified, exit non-zero with a refusal that asks the caller to choose MoM or YoY. An unrecognised growth type is likewise refused, never mapped to a default."
  - "Refusal condition: missing ward, missing category, missing or unknown growth type, a request spanning multiple wards/categories, a missing input file, or an input missing required columns => print an explicit REFUSAL message to stderr and exit non-zero without writing any output file."
