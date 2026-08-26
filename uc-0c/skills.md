# skills.md -- UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads and validates the ward_budget CSV file, reports the total null count
      and identifies exactly which rows have null actual_spend values before returning
      the data for computation.
    input: >
      A file path (str) pointing to a CSV file with the following required columns:
        - period (str, YYYY-MM format): the month of the data
        - ward (str): ward name (5 possible values)
        - category (str): spend category (5 possible values)
        - budgeted_amount (float): always present, never null
        - actual_spend (float or blank): 5 rows are deliberately null
        - notes (str): explains null reasons when actual_spend is blank
    output: >
      A tuple of (data, null_report) where:
        - data (list of dicts): all rows from the CSV with actual_spend parsed
          as float where present, and None where blank
        - null_report (list of dicts): one entry per null row, each containing:
            - period (str)
            - ward (str)
            - category (str)
            - notes (str): the reason from the notes column
      The null_report is printed/logged BEFORE any computation begins. All 5 known
      null rows must appear: 2024-03/Ward 2-Shivajinagar/Drainage & Flooding,
      2024-07/Ward 4-Warje/Roads & Pothole Repair, 2024-11/Ward 1-Kasba/Waste Management,
      2024-08/Ward 3-Kothrud/Parks & Greening, 2024-05/Ward 5-Hadapsar/Streetlight Maintenance.
    error_handling: >
      If the file path does not exist or is unreadable, raise a clear error with the
      file path and exit immediately. If any required column (period, ward, category,
      actual_spend, notes) is missing from the CSV header, refuse with an error naming
      the missing column(s) -- do not attempt to proceed with partial data. If the CSV
      is empty or has only a header row, exit with a warning. Never silently return
      partial data -- if row parsing fails, include the row in the null_report with
      reason "parse error" rather than dropping it.

  - name: compute_growth
    description: >
      Takes a filtered dataset for a specific ward and category plus an explicit
      growth_type argument, and returns a per-period growth table with the formula
      shown alongside every result.
    input: >
      Four arguments:
        - data (list of dicts): the full loaded dataset from load_dataset
        - ward (str): exact ward name to filter on (must match a value in the dataset)
        - category (str): exact category name to filter on (must match a value in the dataset)
        - growth_type (str): must be explicitly "MoM" (month-over-month) or "YoY"
          (year-over-year) -- no default, no inference
    output: >
      A list of dicts (one per period in the filtered dataset), each containing:
        - period (str, YYYY-MM)
        - ward (str)
        - category (str)
        - actual_spend (float or None)
        - previous_spend (float or None): the prior-period value used in the formula
        - growth_rate (str): computed percentage as string (e.g., "+33.1%") or
          "NULL -- not computed: [reason]" when actual_spend or previous_spend is null
        - formula_used (str): the exact formula with values substituted, e.g.,
          "(19.7 - 14.8) / 14.8 * 100 = +33.1%" or "N/A -- null value"
        - notes (str): from the dataset notes column, populated for null rows
      Output must contain one row per month in the filtered period range (12 rows for
      full-year 2024 data), including null rows marked -- never dropped.
    error_handling: >
      If growth_type is not "MoM" or "YoY", refuse immediately with: "ERROR:
      --growth-type must be MoM or YoY. Choosing a formula without user instruction
      is not permitted." Never default to either formula silently.
      If ward or category does not match any row in the dataset, refuse with:
      "ERROR: No data found for ward='[ward]' category='[category]'. Check spelling
      and exact capitalisation." Do not return an empty table silently.
      If a previous period value is null (making growth uncomputable), mark that
      row's growth_rate as "NULL -- not computed: previous period value is null"
      and include it in the output rather than skipping it.
      If the first period has no prior value (e.g., 2024-01 for MoM), mark as
      "NULL -- not computed: no prior period available" -- never compute with
      an assumed baseline of 0.
