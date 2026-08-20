# skills.md — UC-0C Ward Budget MoM Growth Analyzer

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its columns, and reports null
      actual_spend rows with their notes before any computation.
    input: >
      input_path — path to ward_budget.csv.
    output: >
      list of row dicts; prints a FLAG report listing every null row
      (period, ward, category, notes).
    error_handling: >
      Missing file, empty file, or missing required columns (period, ward,
      category, budgeted_amount, actual_spend, notes) reports an error and
      exits without computing.

  - name: compute_growth
    description: >
      Takes the filtered rows for a single ward and category and returns a
      per-period MoM growth table with the formula shown per row.
    input: >
      rows — filtered row dicts (one ward, one category, all periods).
    output: >
      list of output row dicts: period, ward, category, actual_spend,
      previous_actual_spend, growth_pct, formula, flag, notes.
    error_handling: >
      Null actual_spend rows are returned with flag NULL_ACTUAL_SPEND and
      the source note — never computed, never imputed. The first period has
      no previous month and reports growth as blank with an explicit
      formula note.