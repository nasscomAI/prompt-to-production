skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates columns, and reports any null values before returning the data.
    input: File path to the budget dataset CSV (string).
    output: Parsed budget data, along with a count of null values and the specific rows containing them.
    error_handling: Return an error if the file is missing, columns are invalid, or if it cannot be read.

  - name: compute_growth
    description: Calculates the specified growth type for a specific ward and category.
    input: Ward name (string), category (string), and growth_type (string, e.g., 'MoM' or 'YoY').
    output: A per-period table showing the calculated growth with the formula used clearly displayed alongside the result.
    error_handling: Refuse to compute and ask for clarification if growth_type is missing. Refuse if asked to aggregate across wards or categories. Flag null rows and do not compute them, reporting the reason from the notes column.
