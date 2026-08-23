# skills.md — UC-0C Skills

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its required columns, repairs encoding artefacts in string fields, and reports every null actual_spend row with its notes-column reason before returning anything usable.
    input: Filesystem path to a UTF-8 CSV with the exact header period, ward, category, budgeted_amount, actual_spend, notes.
    output: A list of validated row dicts (all six columns as strings, actual_spend kept as raw text so nulls stay detectable) plus a structured null report containing the count of null rows and each row's line number, period, ward, category and notes reason; the null report is printed to stdout before the rows are handed on.
    error_handling: Missing file or a file missing any required column => hard refusal naming the problem and the missing columns, no rows returned. Blank or whitespace-only actual_spend is treated as NULL and flagged, never dropped, never zero-filled. Encoding damage such as double-encoded en dashes in ward names is repaired by cp1252/UTF-8 round-tripping so lookups still match the caller's spelling.

  - name: compute_growth
    description: For exactly one ward and one category, computes growth of actual_spend across periods using only the caller-chosen formula and returns a per-period table in which every row shows the formula applied next to its result.
    input: The validated row list from load_dataset; one ward name and one category name matched against the dataset (dash/en-dash/case tolerant); one growth_type that must be exactly MoM or YoY.
    output: One output row per period sorted by period — period, ward, category, growth_type, actual_spend, previous_period, previous_spend, formula, growth_pct, status, note — suitable for writing straight to growth_output.csv; computed rows carry status COMPUTED with formula strings like (19.7 - 14.8) / 14.8 * 100 and signed percentages such as +33.1% or -34.8%, while impossible rows carry FLAGGED_NULL, PREVIOUS_NULL or NO_BASELINE with an explanatory note.
    error_handling: Missing ward, missing category, or missing/unknown growth_type => refusal with guidance, no output produced; a request for all-ward or all-category figures => explicit aggregation refusal. Ward or category not found in the dataset => lists the valid options instead of guessing. A null current value yields FLAGGED_NULL carrying the notes reason; a null previous value yields PREVIOUS_NULL rather than a fabricated percentage; a period with no baseline (first month for MoM, prior year absent for YoY) yields NO_BASELINE.
