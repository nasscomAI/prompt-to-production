skills:
  - name: load_dataset
    description: Reads the municipal budget CSV and performs initial validation to identify all null spend values and column integrity before processing.
    input:
      type: file
      format: A CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output:
      type: object
      format: A structured dataset accompanied by a report detailing the count and specific locations of null actual_spend values.
    error_handling: Reports the exact ward, category, and period for the 5 deliberate nulls along with their notes; fails if mandatory columns are missing.
  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category while explicitly displaying the mathematical formula used for each row.
    input:
      type: object
      format: Parameters including ward name, category name, and growth_type (e.g., MoM) derived from command-line arguments.
    output:
      type: array
      format: A per-period table including actual spend, calculated growth percentage, and the explicit formula string.
    error_handling: Refuses to compute and flags the row if actual_spend is null; returns a system refusal error if an all-ward aggregation is detected; halts processing if growth_type is not explicitly provided.