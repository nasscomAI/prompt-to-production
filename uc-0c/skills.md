# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates that required columns exist, and reports the total null count and which specific rows are null before returning the dataset.
    input: File path string pointing to the ward_budget.csv file.
    output: A structured list of row dictionaries plus a null_report list identifying each null actual_spend row with its period, ward, category, and notes reason.
    error_handling: Raises an error if the file is missing, if required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent, or if no data rows are found.

  - name: compute_growth
    description: Takes a filtered ward + category slice and a declared growth_type (MoM or YoY), then returns a per-period table with actual_spend, growth rate, the exact formula applied, and NULL flags for missing rows.
    input: A list of filtered row dicts from load_dataset, a growth_type string ("MoM" or "YoY"), and the null_report from load_dataset.
    output: A list of result dicts per period containing: period, actual_spend, growth_rate, formula_shown, and flag (empty or "NULL — [reason]").
    error_handling: Refuses computation if growth_type is not explicitly "MoM" or "YoY"; skips growth calculation for any null row and outputs the flag instead; raises an error if the filtered slice is empty.
