skills:

  - name: load_dataset
    description: Read the ward budget CSV, validate its required columns, count null actual_spend values, and report the affected rows and their notes before returning the dataset.
    input:
      type: CSV dataset
      format: ward_budget.csv
    output:
      type: validated dataset
      format: Dataset with period, ward, category, budgeted_amount, actual_spend, and notes.
    error_handling: Reject the dataset if required columns are missing. Never replace null actual_spend values with zero or invent values.

  - name: compute_growth
    description: Calculate growth for one requested ward and category at the explicitly requested growth type and return a per-period table with the formula shown.
    input:
      type: growth request
      fields:
        - ward
        - category
        - growth_type
    output:
      type: growth table
      format: Per-period results containing period, actual_spend, formula, growth result, and null status or reason where applicable.
    error_handling: Refuse when growth_type is missing, refuse cross-ward or cross-category aggregation, and do not calculate growth for null actual_spend rows.

  - name: validate_growth_output
    description: Verify that the growth output uses the requested ward and category, preserves null rows, shows the formula for every result, and uses the explicitly requested growth type.
    input:
      type: growth output
      format: Per-period growth table.
    output:
      type: validation result
      format: PASS when aggregation level, null handling, formula, and growth type are correct; otherwise FAIL with the violated rule.
    error_handling: Reject outputs with silent null handling, incorrect aggregation level, missing formulas, guessed growth types, or invented values.