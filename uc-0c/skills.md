# skills.md — UC-0C Budget Growth Skills

load_dataset:
  description: >
    Load the ward budget CSV and validate the required columns before
    returning the dataset for calculation.
  inputs:
    - input_csv
  outputs:
    - validated_dataset
    - null_count
    - null_rows
  rules:
    - "Required columns must include period, ward, category, budgeted_amount, actual_spend, and notes."
    - "Report the total number of null actual_spend values before calculation."
    - "Report every null row with its period, ward, category, and notes reason."
    - "Do not replace null actual_spend values with zero or any assumed value."

compute_growth:
  description: >
    Calculate growth for exactly one selected ward and one selected category
    using the explicitly requested growth type.
  inputs:
    - validated_dataset
    - ward
    - category
    - growth_type
  outputs:
    - per_period_growth_table
  rules:
    - "Ward and category must be explicitly specified."
    - "Growth type must be explicitly specified; never guess it."
    - "Only the selected ward and category may be included in the calculation."
    - "For MoM growth use: ((current_actual_spend - previous_actual_spend) / previous_actual_spend) * 100."
    - "If current or previous actual_spend is null, growth must not be computed."
    - "Every output row must show the formula used or the reason calculation was not possible."
    - "Preserve chronological period order."