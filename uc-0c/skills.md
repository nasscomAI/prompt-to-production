skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates column schema, and provides count of null values with reasons.
    input: CSV file path (string) containing columns [period, ward, category, budgeted_amount, actual_spend, notes].
    output: A dataset object and a report of all rows where actual_spend is null, including the reason from the notes column.
    error_handling: Refuse execution if required columns are missing or if the file cannot be read.

  - name: compute_growth
    description: Calculates period-over-period growth for a specific ward and category combination, ensuring no unintended aggregation.
    input: Ward (string), Category (string), growth_type (MoM/YoY), and the loaded dataset.
    output: A table of results including Ward, Category,Period, Actual Spend, Growth Percentage, and the explicit Formula used for each calculation.
    error_handling: 
      - Refuse if growth_type is not provided.
      - Refuse if asked to aggregate across multiple wards or categories (must be specific).
      - For rows with null actual_spend, return "NULL" for the growth value and state the reason from the notes.
