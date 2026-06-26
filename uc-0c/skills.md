# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV data, validates that the required columns are present, and immediately captures the count and details of rows with missing actual_spend.
    input: File path to the budget CSV (string)
    output: A structured tuple including the dataframe/list of dicts, the count of nulls, and the details of which rows (ward + category + notes) were null.
    error_handling: Raise an error if the file cannot be loaded or if ward/category columns are entirely absent.

  - name: compute_growth
    description: Takes a filtered dataset for a specific ward + category + growth_type and returns a per-period table showing the computed growth and the literal formula used.
    input: Filtered dataset (list of dicts or dataframe), target growth type (string: MoM or YoY)
    output: Tabular string or CSV content where each period row contains actual spend, the computed growth percentage, and the verbatim formula used to reach that number.
    error_handling: Return refusal if asked to aggregate everything globally, or if --growth-type is omitted or invalid. Flag records directly if they rely on a null previous period.
