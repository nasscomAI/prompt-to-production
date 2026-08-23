skills:

  - name: load_dataset
    description: Reads the ward budget CSV, validates the required columns, counts null actual_spend values, and reports the affected rows and their notes.
    input: A CSV file containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: Validated dataset information including rows, required columns, null actual_spend count, affected rows, and null reasons from notes.
    error_handling: If the file is missing, unreadable, missing required columns, or malformed, report the problem and do not invent or infer missing data.

  - name: compute_growth
    description: Computes growth for one explicitly requested ward and category using the explicitly requested growth type while preserving one row per period.
    input: Validated dataset plus an explicit ward, category, and growth_type such as MoM.
    output: A per-period table containing period, actual spend, formula used, growth result, and null status where applicable.
    error_handling: If ward, category, or growth_type is missing or invalid, refuse to calculate; if actual_spend is null, flag the row and report its notes reason instead of computing growth.