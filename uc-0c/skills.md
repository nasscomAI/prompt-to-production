skills:
  - name: load_dataset
    description: Parses a budgetary CSV file, audits schemas, and identifies the absolute positions of null rows.
    input: Path string pointing to the source CSV file.
    output: A list of row dictionaries accompanied by an explicit log mapping null items.
    error_handling: Halts cleanly and reports missing essential analytical headers if the format is invalid.

  - name: compute_growth
    description: Calculates Month-over-Month (MoM) budgetary growth patterns for a specified slice with formula tracking.
    input: Parameters defining target ward, category, chosen growth type, and raw record dictionaries.
    output: Generates a scoped output dataframe table containing isolated growth indexes.
    error_handling: Throws a clean refusal error if parameters instruct it to collapse multi-ward records together.
