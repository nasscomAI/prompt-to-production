skills:
  - name: load_dataset
    description: >
      Reads a CSV file containing Ward Budget data. Validates the columns (e.g. `period`, `ward`, `category`, `actual_spend`, `notes`),
      scans for empty `actual_spend` cells (nulls), and outputs an initial diagnostic report indicating 
      the total count of nulls and the specific rows affected before yielding the dataset.
    input:
      type: file path
      format: String path to the target CSV document (e.g., `../data/budget/ward_budget.csv`)
    output:
      type: list of dictionaries
      format: A verified dataset list strictly parsed row by row, ignoring silent type conversion assumptions.
    error_handling: >
      MUST raise a loud warning reporting specifically which rows are missing `actual_spend` data 
      and MUST state their underlying `notes`. It does NOT drop them or impute them.

  - name: compute_growth
    description: >
      Filters dataset to a single requested Ward and Category to prevent silent aggregation loops. 
      Given a growth parameter (e.g., `MoM`), computes accurate sequential variance on `actual_spend`.
      If `actual_spend` is null in the current or previous period, outputs a flag refusal rather than a math error.
    input:
      type: dictionary
      format: { 'dataset': list_of_dicts, 'ward': str, 'category': str, 'growth_type': str }
    output:
      type: list of dictionaries (tabular rows)
      format: A dataset containing the computed growth percentage (e.g. `+33.1%`) and a rigorous 
              formula trail column (e.g. `((19.7 - 14.8) / 14.8) * 100`) alongside the result to prove provenance.
    error_handling: >
      If `growth_type` is None or unspecified, the function immediately terminates execution and throws an error asking the user to specify it. 
      If `actual_spend` logic demands null math, output is flagged strictly with `Must be flagged - not computed`.
