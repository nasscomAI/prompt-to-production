# skills.md

skills:
  - name: load_dataset
    description: >
      Read and validate the ward budget CSV, confirm the required columns,
      identify missing actual_spend values, and report each null row with its
      notes value before returning the dataset.
    input: >
      A path to ward_budget.csv.
    output: >
      A validated dataset containing period, ward, category, budgeted_amount,
      actual_spend, and notes, together with the count and details of null
      actual_spend rows.
    error_handling: >
      If the file is missing, unreadable, malformed, or missing required
      columns, report the problem and stop without inventing or reconstructing
      data.

  - name: compute_growth
    description: >
      Filter the dataset to the explicitly requested ward and category and
      calculate the explicitly requested growth type for each period while
      showing the formula and explicitly flagging periods affected by null
      actual_spend values.
    input: >
      A validated ward budget dataset, a ward name, a category name, and an
      explicitly specified growth type such as MoM.
    output: >
      A per-period table containing the ward, category, period, actual spend,
      previous actual spend where applicable, growth type, formula, growth
      result, status, and null reason where applicable.
    error_handling: >
      Refuse if the ward or category does not exist, if the growth type is not
      specified, or if an all-ward or cross-category aggregation is requested.
      Never replace null values with zero, estimates, averages, or other
      inferred values.