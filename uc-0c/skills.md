# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, and reports null rows before computing growth.
    input: CSV file path to the budget dataset.
    output: A list of valid budget rows plus a null report that includes the affected period, ward, category, and note text.
    error_handling: If required columns are missing or the dataset is malformed, the function raises a validation error instead of producing incorrect output.

  - name: compute_growth
    description: Filters to the requested ward and category, computes growth using the specified growth type, and writes a table including the formula for each row.
    input: Filtered dataset rows, a ward name, a category, and a growth type such as MoM.
    output: A CSV row set showing the monthly values and the growth calculation for each period, with null rows flagged separately.
    error_handling: If the requested scope is broader than one ward and one category or the growth type is missing, the function refuses and returns a clear error instead of guessing.
