# agents.md — UC-0C Number That Looks Right

role: >
  A municipal-budget growth analyst. It computes spend growth for exactly ONE
  ward and ONE category at a time, over the 2024 monthly series in
  data/budget/ward_budget.csv. It never speaks for "all wards" or "all
  categories", never guesses the growth formula, and never hides a missing
  number. It refuses rather than produces a confident-looking wrong answer.

intent: >
  A correct run writes a CSV with exactly these columns —
  period, ward, category, actual_spend, growth_pct, formula, note — containing
  one row per month (12 rows for any complete 2024 ward+category series) and
  NEVER a single aggregated number. For the run
  `--ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM`
  the output must contain, verifiable to 1 decimal:
    * row 2024-07: actual_spend=19.7, growth_pct=33.1, formula=(19.7-14.8)/14.8*100
    * row 2024-10: actual_spend=13.1, growth_pct=-34.8, formula=(13.1-20.1)/20.1*100
    * row 2024-01: growth_pct and formula blank, note='no prior period'
  MoM is defined as (actual_t - actual_{t-1}) / actual_{t-1} * 100, to 1 dp.

context: >
  Inputs allowed: the six columns of ward_budget.csv only
  (period, ward, category, budgeted_amount, actual_spend, notes). budgeted_amount
  is read but is NOT used in any growth computation. 5 rows have a blank
  actual_spend and a human reason in notes. Ward strings contain a non-ASCII
  en dash (U+2013), e.g. 'Ward 1 – Kasba' — match byte-for-byte, never
  normalise dashes. The dataset spans only 2024, so year-over-year has no prior
  year. No external data, no network, no LLM/API at runtime — logic is
  deterministic and rule-based. Standard library only.

enforcement:
  # --- E1: refuse aggregation across wards or categories -------------------
  - >
    AGGREGATION REFUSAL. If --ward or --category is omitted, blank, or equals
    any aggregate token — 'all', '*', 'every', 'total', 'any', 'overall',
    'all wards', 'all categories' (case-insensitive) — the system REFUSES: it
    prints 'REFUSED: ...' to stderr including the offending token, exits with
    code 3, and writes NO output file. A single aggregated number or a single
    averaged row must never appear in growth_output.csv.
    TEST: `--ward all` exits 3, stderr contains 'REFUSED' and 'all', and
    growth_output.csv is not (re)written for that run.

  # --- E2: flag every null before computing -------------------------------
  - >
    NULL FLAGGING. Before any growth math runs, the loader scans every row and
    collects those whose actual_spend is blank. It prints a null report to
    stdout listing each as 'period | ward | category | reason: <notes>'. For
    the shipped dataset this report must name exactly 5 null rows, including
    '2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding | reason: Data not
    submitted by ward office'. A null row is never silently dropped.
    TEST: every run's stdout contains '5 NULL actual_spend row(s) found' and
    the string 'Ward 2 – Shivajinagar'.

  # --- E3: null rows appear in the output, flagged, not computed ----------
  - >
    NULL IN OUTPUT. Any null actual_spend row that belongs to the selected
    ward+category appears in growth_output.csv with actual_spend, growth_pct
    and formula ALL blank, and note equal to 'NULL — <reason from notes>'. It
    is never skipped and never assigned a fabricated growth number.
    TEST: for `--ward "Ward 2 – Shivajinagar" --category "Drainage & Flooding"
    --growth-type MoM`, the 2024-03 row has growth_pct='' and
    note='NULL — Data not submitted by ward office'.

  # --- E4: formula shown on every computed row ----------------------------
  - >
    FORMULA TRANSPARENCY. Every output row with a non-empty growth_pct MUST
    also carry the exact formula string in the formula column, in the form
    '(actual_t-actual_{t-1})/actual_{t-1}*100' using the real numbers, e.g.
    '(19.7-14.8)/14.8*100'. A row may never carry a result without its
    formula, nor a formula without its result. Rows with no computation
    (first period, null, YoY-N/A, prior-period-null) have BOTH growth_pct and
    formula blank.
    TEST: in any MoM output, the set of rows where growth_pct != '' equals the
    set where formula != ''; the 2024-07 Ward1/Roads formula is exactly
    '(19.7-14.8)/14.8*100'.

  # --- E5: growth-type is explicit, never guessed -------------------------
  - >
    GROWTH-TYPE REFUSAL. If --growth-type is omitted or is not exactly 'MoM' or
    'YoY' (case-sensitive), the system REFUSES: stderr 'REFUSED: ...', exit 3,
    no output written. The system never defaults to MoM and never silently
    picks one formula over another.
    TEST: omitting --growth-type exits 3; `--growth-type QoQ` exits 3;
    `--growth-type mom` (lowercase) exits 3.

  # --- E6: ward/category must exist and be matched exactly ----------------
  - >
    EXACT-MATCH REFUSAL. Ward and category are matched byte-for-byte against
    the data (en dash U+2013 preserved). If the requested ward or category
    matches zero rows, the system REFUSES (exit 3) and prints the list of
    valid wards/categories so the caller can correct the spelling — it never
    returns an empty file masquerading as 'no growth'.
    TEST: `--ward "Ward 1 - Kasba"` (ASCII hyphen) exits 3 with a message
    listing the valid wards.

  # --- E7: output shape is a per-month table, never one number ------------
  - >
    PER-SERIES SHAPE. The output is always one data row per period for the
    single chosen ward+category — at most 12 rows for 2024 plus the header —
    never a single scalar. YoY over a 2024-only dataset is not silently
    dropped: every row is emitted with growth_pct blank and note
    'YoY N/A — dataset spans only 2024 (no prior year)'.
    TEST: Ward1/Roads MoM yields exactly 12 data rows; Ward1/Roads YoY also
    yields 12 data rows, all with growth_pct=''.
