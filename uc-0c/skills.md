# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Loads the ward budget CSV file, validates the expected schema, identifies
      all wards and categories, and performs a pre-computation scan to detect
      and log all rows with null actual_spend values along with their notes.
    input: >
      input_path (str) — path to ward_budget.csv (e.g., ../data/budget/ward_budget.csv).
    output: >
      A tuple containing:
      (1) records (list of dicts containing parsed row data: period, ward, category,
      budgeted_amount as float, actual_spend as float or None, notes as str),
      (2) null_records (list of dicts detailing each row where actual_spend is null).
    error_handling: >
      If the input file does not exist or has invalid encoding, report error and exit.
      If required columns (period, ward, category, budgeted_amount, actual_spend, notes)
      are missing, raise an informative schema error.

  - name: compute_growth
    description: >
      Calculates per-period budget growth (such as MoM) for an explicitly
      specified ward and category. Enforces non-aggregation, transparent formula
      substitution, and explicit null flagging without silent zero-substitution.
    input: >
      records (list of dicts from load_dataset),
      ward (str — target ward name),
      category (str — target budget category),
      growth_type (str — 'MoM' or 'YoY'),
      output_path (str — path for output CSV file).
    output: >
      Writes a CSV file to output_path containing columns:
      ward, category, period, budgeted_amount, actual_spend, growth_type,
      growth_pct, formula, notes. Returns the list of output row dicts.
    error_handling: >
      If ward or category is missing or set to 'All', REFUSE execution with an
      explicit error message prohibiting cross-ward/category aggregation.
      If growth_type is missing, empty, or unsupported, REFUSE execution and
      prompt the user for a valid growth type ('MoM').
      If actual_spend for a period is null, record growth_pct as 'NULL' and
      formula as 'Not computed (null actual_spend)', logging the note.
      If previous period's spend is null or non-existent, record growth_pct
      as 'n/a' and provide an explanatory formula note.
