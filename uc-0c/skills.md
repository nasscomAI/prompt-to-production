# skills.md — UC-0C Budget Growth Calculator Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required schema columns, checks for missing data, and logs all null actual_spend rows with their associated notes.
    input: File path to ward budget CSV dataset (--input).
    output: Processed dataset object alongside detailed audit log of null row positions and note reasons.
    error_handling: Detects missing CSV file or invalid column headers, raising a schema validation error before processing begins.

  - name: compute_growth
    description: Computes period-over-period growth for a specified ward and category based on growth type, outputting a table with period, actual spend, growth percentage, calculation formula, and null flags.
    input: Dataset object, ward name (--ward), category name (--category), growth type (--growth-type), and output file path (--output).
    output: Writes growth_output.csv with per-period metric results, explicit formula annotations, and flagged null reasons.
    error_handling: Refuses calculation if growth_type is missing or if ward/category parameters attempt cross-group aggregation.
