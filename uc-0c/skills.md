skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the expected columns, and reports the count of null values along with identifying the specific null rows before returning the data.
    input: File path to the CSV dataset (string).
    output: Validated dataset object, null value count (integer), and a list/report of rows containing nulls with their corresponding notes.
    error_handling: System must fail gracefully if the file is missing or if the required schema dimensions (period, ward, category, budgeted_amount, actual_spend, notes) are absent.

  - name: compute_growth
    description: Calculates growth metrics for a given dataset segment based on a specific ward, category, and growth type, ensuring formulas are transparently included in the output.
    input: Validated dataset, ward name (string), category name (string), and growth_type (string, e.g., MoM, YoY).
    output: A per-period table (or dataframe) showing the period, actual_spend, computed growth metric, and the exact formula used.
    error_handling: Refuses to execute and prompts the user if --growth-type is missing (never guesses). Handles deliberately null 'actual_spend' values by flagging them, appending the null reason from the 'notes' column, and bypassing calculation for those specific periods. Refuses to compute if asked to aggregate across multiple wards or categories.
