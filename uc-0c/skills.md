skills:
  - name: load_dataset
    description: >
      Reads the budget CSV, validates that the required columns are present, and
      reports every null actual_spend row with its reason before returning.
    input: >
      csv_path (str) — path to ward_budget.csv with columns period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      tuple (rows, nulls). rows is a list of dicts in source order with
      actual_spend parsed to float or None. nulls is a list of dicts naming
      period, ward, category and the reason quoted from the notes column.
      The null report is printed before any computation happens.
    error_handling: >
      A missing or unreadable file exits with the path named. A file lacking any
      required column exits naming the missing columns rather than failing later
      on a KeyError. A row whose actual_spend cannot be parsed as a number is
      treated as null and reported, not silently coerced to zero, because zero is
      a real spend value and would corrupt every growth figure that touches it.

  - name: compute_growth
    description: >
      Computes period-over-period growth for exactly one ward and one category,
      returning a per-period table that shows the formula behind every figure.
    input: >
      rows (from load_dataset); ward (str); category (str); growth_type
      (MoM or YoY).
    output: >
      list of dicts in period order, each with period, ward, category,
      actual_spend, previous_period, previous_spend, growth_type, growth_pct,
      formula and flag. growth_pct is blank where a flag is set.
    error_handling: >
      Refuses when growth_type is absent, when the ward or category is not
      present in the dataset, or when a request would span more than one ward or
      category, naming what is required or what is available. A period whose own
      or whose prior actual_spend is null yields a flagged row with the reason
      and no growth figure, never an imputed one. YoY against a single-year
      dataset yields flagged rows reporting that no prior-year period exists.
