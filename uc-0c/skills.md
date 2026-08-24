# skills.md — UC-0C Budget Growth Analyser

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its structure, and reports every null actual_spend row with its notes reason before any computation happens.
    input: Path to a UTF-8 CSV with the required columns period (YYYY-MM), ward, category, budgeted_amount, actual_spend (float or blank), notes.
    output: The parsed rows plus three derived artefacts — the sorted list of distinct ward strings, the sorted list of distinct category strings, and a null report (count + period/ward/category/notes for each blank actual_spend).
    error_handling: A missing or unreadable file, or missing required columns, aborts with a clear error before anything is processed; blank actual_spend is recorded in the null report, not treated as zero; unparseable numeric values are flagged per-row instead of crashing.

  - name: compute_growth
    description: Computes the growth series for exactly one ward and one category using the requested growth type, returning a per-period table where every row shows its formula or its flag.
    input: The loaded dataset rows, an exact ward string, an exact category string, and a growth type — MoM (vs previous month) or YoY (vs same month previous year); the ward and category must match dataset values exactly.
    output: One row per period containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_pct (1 decimal, signed), formula (with substituted values), flag, and notes. Rows that cannot be computed carry one of NO_PRIOR_PERIOD (first month / no prior year), NULL_SPEND (this row's spend is null, reason from notes), PRIOR_SPEND_NULL (comparison operand was null, reason from prior row's notes), PRIOR_SPEND_ZERO (growth undefined against a zero operand), or UNPARSEABLE_SPEND — with growth_pct and formula left empty.
    error_handling: Refuses rather than guesses when growth type is absent from the input or not one of MoM/YoY, when the ward or category is not an exact dataset value (returns the valid options), and when the request spans multiple wards/categories; never imputes nulls, never substitutes budgeted_amount for actual_spend, and leaves uncomputable rows visibly flagged.
