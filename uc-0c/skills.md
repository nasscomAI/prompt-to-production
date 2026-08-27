# skills.md — UC-0C Number That Looks Right
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: >
      Reads a ward budget CSV, validates required columns exist (period, ward,
      category, budgeted_amount, actual_spend, notes), reports total row count,
      and identifies how many actual_spend values are null along with their
      period, ward, category, and notes explanation before returning the data.
    input: >
      A file path (string) pointing to a CSV with columns: period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      A pandas DataFrame with parsed columns (actual_spend as float, NaN for
      blanks) — after printing a validation report to stderr that includes
      total rows, column presence check, null count, and a table of null rows
      with their period, ward, category, and notes.
    error_handling: >
      If the file does not exist, raise FileNotFoundError. If required columns
      are missing, raise ValueError listing which columns are absent.

  - name: compute_growth
    description: >
      Filters the dataset to a single ward + category, sorts by period, and
      computes the specified growth type (currently only MoM) for each period.
      Returns a table where every row includes the actual_spend, growth rate,
      the exact formula used, a null_flag, and the null_reason if applicable.
    input: >
      A pandas DataFrame (from load_dataset), a ward string, a category string,
      and a growth_type string ("MoM").
    output: >
      A pandas DataFrame with columns: period, actual_spend, growth_rate,
      formula, null_flag, null_reason. The growth_rate for the first period
      is "N/A" (no previous period). Rows with null actual_spend have
      null_flag = True and growth_rate = "", with null_reason from the notes.
    error_handling: >
      If the ward+category combination yields zero rows, raise ValueError.
      If growth_type is not "MoM", raise ValueError describing the only
      supported growth type. If filtering produces unexpected duplicate
      period entries, raise ValueError.
