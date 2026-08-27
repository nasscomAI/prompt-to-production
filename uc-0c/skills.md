# skills.md

skills:
  - name: load_dataset
    description: Reads the financial CSV, validates structure, and reports the specific locations and count of all null 'actual_spend' values before processing.
    input: CSV file path
    output: Cleaned and validated DataFrame or list of records
    error_handling: Refuses if columns are missing or if file is not found. Reports null rows explicitly.

  - name: compute_growth
    description: Calculates month-over-month (MoM) or year-over-year (YoY) growth for a specific ward and category.
    input: ward (string), category (string), growth_type (MoM/YoY), data
    output: Table showing Period, Actual Spend, Growth Percentage, and Formula used.
    error_handling: Refuses if growth_type is missing. Skips null periods with a specific warning including the reason from the 'notes' column.
