 skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the required columns, counts
      missing actual_spend values, and reports every null row with its
      period, ward, category, and notes before calculations begin.

    input:
      type: CSV file
      required_columns:
        - period
        - ward
        - category
        - budgeted_amount
        - actual_spend
        - notes

    output:
      type: structured dataset
      includes:
        - validated rows
        - null actual_spend count
        - null row details
        - validation status

    rules:
      - "Do not replace null actual_spend values."
      - "Report the notes value for every null actual_spend row."
      - "Do not aggregate the dataset during loading."

  - name: compute_growth
    description: >
      Takes one ward, one category, and an explicitly specified growth_type,
      then returns a per-period growth table with the formula used for every
      calculation.

    input:
      type: structured dataset
      parameters:
        - ward
        - category
        - growth_type

    output:
      type: per-period table
      fields:
        - period
        - ward
        - category
        - actual_spend
        - previous_actual_spend
        - formula
        - growth
        - status
        - null_reason

    rules:
      - "Filter to exactly the requested ward and category."
      - "Never combine different wards or categories."
      - "For MoM, compare each period with the immediately preceding period."
      - "If either required actual_spend value is null, mark the calculation NOT_COMPUTED."
      - "Show the formula in every output row."
      - "Require growth_type explicitly; never infer or guess it."