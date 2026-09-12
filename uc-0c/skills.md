# skills.md — UC-0C

skills:

  - name: load_dataset
    description: Read the budget CSV, validate required columns, report the total null count and identify every row with a null actual_spend value.
    input: A CSV file path containing period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: A validated structured dataset plus the null count and details of every null actual_spend row, including its period, ward, category, and notes reason.
    error_handling: If the file is missing, unreadable, or required columns are missing, report the error and do not calculate growth.

  - name: compute_growth
    description: Calculate growth for the explicitly requested ward and category using the explicitly supplied growth type and show the formula for every result.
    input: A validated dataset, one ward, one category, and an explicitly specified growth type such as MoM.
    output: A per-period table for the requested ward and category containing actual spend, formula used, growth result, and null flags with reasons where actual_spend is missing.
    error_handling: Refuse if the growth type is missing, the request asks for all-ward or cross-category aggregation, or required data is null for a calculation; flag null rows instead of computing them.