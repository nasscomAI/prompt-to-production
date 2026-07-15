# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV file, validates that required columns are
      present, identifies and reports null actual_spend rows before returning
      the full dataset as a list of row dicts.
    input: >
      A string: the file path to the CSV file
      (e.g. "../data/budget/ward_budget.csv").
      Expected columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    output: >
      A dict with two keys:
        - rows (list of dicts): All rows from the CSV. Each dict has keys:
          period (string, YYYY-MM), ward (string), category (string),
          budgeted_amount (float), actual_spend (float or None), notes (string).
        - null_report (list of dicts): One entry per null actual_spend row, each
          with: period, ward, category, null_reason (taken from notes column).
      The null_report is always printed to stdout before the caller proceeds.
    error_handling: >
      If the file does not exist: print a clear error message including the path
      and exit with code 1. Do not return partial data.
      If any required column is missing: print which columns are missing and
      exit with code 1.
      If actual_spend cannot be parsed as a number for a row: treat it as null,
      include it in null_report, and log the row's period and ward to stdout.
      Never silently skip a row.

  - name: compute_growth
    description: >
      Takes a filtered set of rows (single ward + single category), a growth
      type (MoM or YoY), and returns a per-period growth table with formula
      shown for each computed row and null rows clearly flagged.
    input: >
      A dict with keys:
        - rows (list of dicts): Pre-filtered rows for a single ward and category,
          as returned by load_dataset, sorted by period ascending.
        - growth_type (string): Must be exactly "MoM" or "YoY".
        - ward (string): The ward name being analysed (used in output labelling).
        - category (string): The category name being analysed.
    output: >
      A list of dicts, one per period, each with:
        - period (string): YYYY-MM
        - ward (string)
        - category (string)
        - actual_spend (float or None)
        - growth_value (float or None): None if actual_spend is null or if there
          is no prior period to compute against (i.e. first row).
        - formula_used (string or None): e.g. "(19.7 - 14.8) / 14.8 × 100".
          None if growth_value is None.
        - null_flag (string): "NULL — {null_reason}" if actual_spend is null,
          else "FIRST_PERIOD" for the first row, else empty string "".
    error_handling: >
      If growth_type is not "MoM" or "YoY": raise ValueError with message:
      "Growth type not specified. Please provide growth_type='MoM' or 'YoY'.
      No computation performed."
      If rows list is empty: return an empty list and print a warning to stdout
      including the ward and category names.
      If two consecutive periods are non-null but the prior period's spend is
      zero: set growth_value to None, formula_used to "(division by zero —
      prior period spend is 0)", and null_flag to "COMPUTATION_ERROR".
