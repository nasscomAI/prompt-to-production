skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports any null values count and rows before returning the data.
    input: Filepath to the CSV data (e.g., ../data/budget/ward_budget.csv) and expected schema details.
    output: A validated dataset object/table, along with a report detailing the count of nulls and the specific rows they appear in.
    error_handling: If file not found or schema validation fails, throw an error.

  - name: compute_growth
    description: Calculates growth (e.g., MoM, YoY) for a specific ward and category over time.
    input: Dataset, Ward (string), Category (string), and growth_type (string).
    output: A per-period table showing the calculated growth values, with an explicit string representation of the mathematical formula used for every row.
    error_handling: If growth_type is omitted or invalid, refuse execution and prompt the user. Refuse requests to aggregate across multiple wards or categories. If a null value is encountered, report the null reason from the notes column and skip calculation for that row.
