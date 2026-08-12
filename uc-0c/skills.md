# skills.md — UC-0C Ward Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that every required column is
      present, and reports the null actual_spend rows with their reasons
      before returning any data for computation.
    input: >
      path (str) — path to data/budget/ward_budget.csv. Expected columns:
      period (YYYY-MM), ward (str), category (str), budgeted_amount (float),
      actual_spend (float or empty), notes (str).
    output: >
      A dict with keys: rows (list of parsed row dicts in file order, with
      actual_spend as float or None), wards (sorted unique list), categories
      (sorted unique list), periods (sorted unique list), and null_rows (list
      of {period, ward, category, note} for every row whose actual_spend is
      empty). The null report is printed to stdout before the dict is
      returned, so nulls are visible whether or not the caller inspects them.
    error_handling: >
      Missing file or unreadable path: exits with the path named, before any
      output file is created.
      Missing required column: exits listing the columns actually found. The
      run does not proceed on a partial schema, because a growth table
      computed from an incomplete file looks identical to a correct one.
      Empty actual_spend (silent-null failure mode): parsed as None, never as
      0.0 and never backfilled from budgeted_amount. Recorded in null_rows
      with the verbatim notes text.
      actual_spend present but non-numeric: parsed as None and recorded in
      null_rows with the reason "unparseable value: <raw>", so a corrupt cell
      is treated with the same visibility as an empty one.
      Duplicate (period, ward, category) keys: reported, and the first
      occurrence is used, because silently summing duplicates would be an
      undeclared aggregation.
      Zero rows parsed: exits rather than returning an empty dataset that
      would produce an empty but clean-looking growth table.

  - name: compute_growth
    description: >
      Computes period-over-period growth in actual_spend for one ward and one
      category, returning one row per period with the substituted arithmetic
      shown alongside each result.
    input: >
      dataset (dict from load_dataset), ward (str, exact dataset value),
      category (str, exact dataset value), growth_type (str, "MoM" or "YoY").
      All four are required; growth_type has no default.
    output: >
      A list of row dicts with keys ward, category, period, budgeted_amount,
      actual_spend, prior_period, prior_actual_spend, growth_type, formula,
      growth_pct, status, note. One row per period in the dataset range,
      including the first period and every uncomputable period. growth_pct is
      rounded to one decimal place; formula contains the substituted operands.
    error_handling: >
      growth_type not supplied (formula-assumption failure mode): the caller
      refuses before this skill runs. compute_growth itself rejects any value
      other than MoM or YoY rather than defaulting.
      Ward or category not present in the dataset: raises a refusal listing the
      valid values. No fuzzy or closest-match selection — dash and whitespace
      normalisation only, which is a formatting equivalence, not a guess.
      First period of the series: emitted with status NO_PRIOR_PERIOD and an
      empty growth_pct, never omitted from the table and never shown as 0%.
      Current period null: status NOT_COMPUTED_NULL_CURRENT, growth_pct blank,
      note carrying the verbatim source note.
      Prior period null (null-propagation failure mode): status
      NOT_COMPUTED_PRIOR_NULL even though the current value exists, with the
      prior period's note quoted. One null invalidates two rows and both say so.
      Prior actual_spend of exactly 0.0: status NOT_COMPUTED_ZERO_BASE rather
      than a division-by-zero crash or an infinite percentage.
      YoY requested against a single-year dataset: every row returns
      NOT_COMPUTED_NO_PRIOR_YEAR with the dataset coverage stated. The skill
      never falls back to MoM.
      Any request whose scope spans more than one ward or category: refused by
      the caller before this skill is reached; this skill has no code path that
      sums across either dimension.
