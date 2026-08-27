# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates row health, and reports identified null Actual Spend values before returning the dataset.
    input: File path to a budget CSV.
    output: A list of row dictionaries containing: period, ward, category, budgeted_amount, actual_spend, notes.
    error_handling: Return error if file is missing; print summary of null rows found in the logs.

  - name: compute_growth
    description: Calculates sequential growth (MoM) for a specific ward and category, flagging nulls and citing formulas.
    input: A filtered dataset, ward name, category name, and growth type.
    output: A collection of output records containing: period, actual_spend, growth_percent, formula, notes.
    error_handling: Refuse and return early if ward or category are not specified; if actual_spend or the previous value is NULL, set growth to 'NULL' and append notes.
