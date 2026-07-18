# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward_budget CSV, validates that all six required columns are
      present, and surfaces every NULL actual_spend row BEFORE any growth is
      computed — so a missing number can never be silently skipped.
    input: >
      A filesystem path to a CSV (string or pathlib.Path). Resolved from the
      script's own location via __file__ when --input is omitted, so the same
      command works from the repo root and from inside uc-0c/. Expected
      columns: period(YYYY-MM), ward, category, budgeted_amount,
      actual_spend (may be blank), notes.
    output: >
      A tuple (rows, null_rows, wards, categories):
        * rows       — list of dict rows, the full dataset (typically 300 rows).
        * null_rows  — list of {period, ward, category, notes} for every row
                       whose actual_spend is blank (5 for the shipped dataset).
        * wards      — sorted list of distinct ward strings.
        * categories — sorted list of distinct category strings.
      As a side effect it prints a human-readable null report to stdout
      ('N NULL actual_spend row(s) found' + one line per null row with its
      reason from notes).
    error_handling: >
      If the file does not exist, prints 'ERROR: input file not found' to
      stderr and exits 2. If any required column is missing, prints
      'ERROR: input CSV is missing required column(s): ...' to stderr and
      exits 2. A blank actual_spend is NOT an error — it is collected into
      null_rows and reported, never raised and never skipped.

  - name: compute_growth
    description: >
      Filters the dataset to exactly ONE ward and ONE category, sorts by
      period, and returns a per-month growth table with the formula shown on
      every computed row. Never aggregates across wards or categories.
    input: >
      (rows, ward, category, growth_type) where rows is the dataset from
      load_dataset; ward and category are single exact strings (en dash U+2013
      preserved, matched byte-for-byte); growth_type is 'MoM' or 'YoY'
      (validated upstream — anything else is refused before this skill runs).
    output: >
      A list of result dicts, one per period in ascending period order, each
      with keys: period, ward, category, actual_spend, growth_pct, formula,
      note. For MoM, growth_pct = (actual_t - actual_{t-1}) / actual_{t-1} * 100
      rendered to 1 decimal, and formula is the literal string e.g.
      '(19.7-14.8)/14.8*100'. For a 2024-only dataset, YoY rows carry
      growth_pct='' and note='YoY N/A — dataset spans only 2024 (no prior year)'.
    error_handling: >
      Aggregation / unknown growth-type / non-existent ward or category are
      refused upstream (exit 3) before this skill is called — compute_growth
      itself always receives a valid single ward, single category and a known
      growth_type. Within the series it handles three non-computable cases
      deterministically rather than guessing:
        * actual_spend blank  -> growth_pct/formula blank, note='NULL — <reason>'.
        * first period (MoM)  -> growth_pct/formula blank, note='no prior period'.
        * prior period NULL   -> growth_pct/formula blank,
                                 note='prior period actual_spend is NULL — growth not computed'.
      It never fabricates a number to fill a blank, and never divides by zero.
