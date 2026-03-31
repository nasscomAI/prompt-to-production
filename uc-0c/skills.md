skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports the count and details of null actual_spend rows before returning the dataset.
    input:
      type: string
      format: File path to the ward_budget.csv containing columns period, ward, category, budgeted_amount, actual_spend, notes.
    output:
      type: object
      format: Dictionary containing a pandas DataFrame of all rows and a list of null row records (period, ward, category, notes) for pre-computation flagging.
    error_handling: >
      Aborts with a clear error if the file does not exist or cannot be read.
      Aborts if any required column (period, ward, category, actual_spend, notes) is missing.
      Reports the exact count and details of null actual_spend rows before returning —
      never silently skips nulls or proceeds without flagging them.

  - name: compute_growth
    description: Takes a loaded dataset filtered to one ward and one category, computes per-period growth using the specified growth type, and returns a table with the formula shown for every row.
    input:
      type: object
      format: Dictionary with keys — data (DataFrame filtered to one ward and category), ward (string), category (string), growth_type (string, must be MoM or YoY).
    output:
      type: file
      format: CSV file with columns period, ward, category, actual_spend, growth_value, formula, flag — where flag is NULL_FLAGGED for null rows and formula shows the exact calculation used.
    error_handling: >
      Refuses and exits with an error message if growth_type is not MoM or YoY — never defaults silently.
      Refuses and exits if ward or category is not found in the dataset.
      Marks null actual_spend rows as NULL_FLAGGED in the output and skips growth computation for those rows.
      Never returns a single aggregated number — output must always be a per-period table.