skills:
  - name: analyze_budget_variance
    description: Calculate budget-versus-actual variance for each valid budget record.
    input: A CSV row containing period, ward, category, budgeted_amount, actual_spend, and notes.
    output: A structured result containing the original identifying fields, variance, and status.
    error_handling: If actual_spend is missing, do not calculate a variance and mark the row as MISSING_ACTUAL; if required fields are invalid, mark the row as INVALID.

  - name: batch_budget_analysis
    description: Read the complete budget CSV and produce a report of variances, overspending, and missing actual-spend records.
    input: Input CSV path and output report path.
    output: A text report containing calculated variances, significant overspending records, and explicit missing-data records.
    error_handling: Do not crash on a bad row; report the affected row as invalid and continue processing the remaining rows.