# skills.md
skills:
  - name: load_dataset
    description: >
      Loads the ward budget dataset and validates that all required columns
      are present while reporting rows containing null actual_spend values.
    input: >
      Path to ward_budget.csv dataset.
    output: >
      Structured dataset containing rows for period, ward, category,
      budgeted_amount, actual_spend, and notes.
    error_handling: >
      If required columns are missing or the dataset cannot be read,
      stop execution and return an error message.

  - name: compute_growth
    description: >
      Calculates period growth for a specified ward and category using the
      requested growth type.
    input: >
      Dataset rows filtered by ward and category plus growth_type (MoM or YoY).
    output: >
      A per-period table showing period, actual_spend, growth value, and the
      formula used to compute the growth.
    error_handling: >
      If actual_spend is null for a row, flag it and skip growth calculation
      while reporting the reason from the notes column.