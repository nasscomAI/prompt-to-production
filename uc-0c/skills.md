# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates required columns exist, and reports null count and which specific rows have null actual_spend before returning the data.
    input: >
      File path (string) to a CSV file with expected columns: period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      A tuple of: (1) list of row dictionaries from the CSV, (2) a list of
      null-row reports containing period, ward, category, and notes for each
      row where actual_spend is blank/null. Console output shows total rows,
      unique wards, unique categories, and null row details.
    error_handling: >
      If file does not exist or is unreadable, print error and exit.
      If required columns are missing, print which columns are missing and exit.
      If the file has zero data rows, print error and exit.

  - name: compute_growth
    description: Takes a filtered dataset (single ward + category), a growth type (MoM or YoY), and computes per-period growth with formula shown in every row.
    input: >
      Parameters: ward (string), category (string), growth_type (string: "MoM" or "YoY"),
      and the loaded dataset rows.
    output: >
      A list of dictionaries, each with: period, ward, category, actual_spend,
      previous_period, previous_spend, growth_pct (rounded to 1 decimal),
      formula (string showing exact calculation), flag (null reason or empty).
      First period shows "N/A — no previous period" for growth.
      Null rows show "NULL — [reason from notes]" for growth.
    error_handling: >
      If no rows match the specified ward + category, print error listing available
      wards and categories, then exit. If growth_type is not "MoM" or "YoY",
      refuse and print accepted values.
