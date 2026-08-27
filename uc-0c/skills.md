# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns, and explicitly reports the count and specific rows containing null actual_spend values.
    input: file_path (string) - The path to the ward_budget.csv file.
    output: dataset (dataframe/object) - A validated data structure containing budget records.
    error_handling: Refuses if the file is missing or if mandatory columns (period, ward, category, actual_spend) are not found.

  - name: compute_growth
    description: Calculates per-period growth (MoM or YoY) for a specific ward and category, returning a table that includes the calculation formula for every result.
    input: ward (string), category (string), growth_type (string: "MoM" or "YoY").
    output: growth_table (list/table) - A per-period breakdown of spend, growth percentage, and the specific formula used.
    error_handling: Refuses if growth_type is missing or if requested to aggregate across different wards or categories.
