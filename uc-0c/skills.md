# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates columns, and reports the count and specific details of null actual_spend rows before returning the data.
    input:
      type: string
      format: File path to the input CSV file (e.g., ../data/budget/ward_budget.csv).
    output:
      type: object
      format: Parsed dataset records along with a validation summary listing total null rows, their locations (ward, category, period), and the reason for the null values from the notes column.
    error_handling: Refuses execution and reports an error if the file is missing, cannot be parsed, or if key columns (period, ward, category, budgeted_amount, actual_spend, notes) are missing or misaligned.

  - name: compute_growth
    description: Calculates growth for a specified ward and category based on the growth type, returning a per-period table that includes the formula used for each result.
    input:
      type: object
      format: |
        A dictionary containing:
          - dataset: The validated dataset from load_dataset.
          - ward: String specifying a single ward (e.g., "Ward 1 – Kasba").
          - category: String specifying a single category (e.g., "Roads & Pothole Repair").
          - growth_type: String specifying the calculation method (e.g., "MoM", "YoY").
    output:
      type: array
      format: A per-period list of records containing period, ward, category, actual spend, calculated growth rate, and the exact formula applied to compute the growth rate.
    error_handling: |
      - Refuses execution and asks for clarification if the growth_type is unspecified or ambiguous.
      - Refuses to calculate and flags any target row with a null actual_spend, reporting the corresponding reason from the notes column.
      - Refuses and rejects any requests that attempt to aggregate actual spend across multiple wards or categories.
