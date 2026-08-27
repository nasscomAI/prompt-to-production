# skills.md — UC-0C Budget Growth Skills

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates required columns exist, reports
      total row count and the exact rows where actual_spend is null (with
      their notes/reason), and returns a clean DataFrame.
    input: >
      filepath: str — path to ward_budget.csv
    output: >
      pandas DataFrame with columns [period, ward, category, budgeted_amount,
      actual_spend, notes]. Also prints a null report to stdout.
    error_handling: >
      Raises ValueError if required columns are missing or file not found.
      Prints null rows with period, ward, category, and notes.

  - name: compute_growth
    description: >
      Filters data to one ward + one category, sorts by period, computes
      growth (MoM or YoY) using actual_spend, flags null periods, and
      attaches the formula string to each row.
    input: >
      df: DataFrame, ward: str, category: str, growth_type: str ("MoM" or "YoY")
    output: >
      DataFrame with columns [period, ward, category, budgeted_amount,
      actual_spend, growth, formula, notes]. For null actual_spend, growth is
      "NULL — not computed" and formula explains why.
    error_handling: >
      Raises ValueError if growth_type is not "MoM" or "YoY". Returns empty
      DataFrame if ward/category not found. For YoY with single year of data,
      warns that no prior-year data exists.
