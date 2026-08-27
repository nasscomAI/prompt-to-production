skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates columns, and reports the null count and specific rows with nulls before returning the data.
    input:
      type: string
      format: File path to the dataset CSV file
    output:
      type: object
      format: Parsed dataset along with a pre-computation report identifying the count and specific details of rows with null actual_spend values.
    error_handling: Halts execution if expected columns are missing, and strictly flags every null row with its corresponding note before any computation occurs.
  - name: compute_growth
    description: Computes the specified growth metric for a single ward and category over time, appending the exact formula used to each output row.
    input:
      type: object
      format: Contains ward (string), category (string), and growth_type (string) parameters.
    output:
      type: array of objects
      format: Per-period table containing period, actual_spend, computed growth metric, and a string representation of the applied formula.
    error_handling: Refuses to run and prompts the user if growth_type is missing; refuses and returns an error if input implies aggregating across multiple wards or categories; flags and skips computation for any periods with null actual_spend.
