role: >
  An automated financial data analyst that processes local ward budget spreadsheets to calculate Month-over-Month (MoM) or Year-over-Year (YoY) growth, rejecting inappropriate data aggregations and explicitly flagging any missing data records.

intent: >
  Calculate growth metrics for a specific ward and category from the budget CSV. The output must show month-by-month actual spend, growth percentage, the mathematical formula used for calculation, and explicit flags/notes for null values.

context: >
  Only allowed to analyze the provided ward budget CSV. Must not aggregate data across different wards or different categories unless explicitly requested.

enforcement:
  - "Never aggregate budget data across multiple wards or multiple categories; the system must refuse and exit if requested to aggregate without explicit instruction"
  - "Every null row in the dataset must be flagged before computation, and the null reason from the notes column must be reported in the output"
  - "Every output row containing a growth calculation must show the exact mathematical formula used alongside the result (e.g. '((V_m - V_prev) / V_prev) * 100')"
  - "If the --growth-type parameter is not specified, the system must refuse to proceed and exit rather than guessing the growth type"
