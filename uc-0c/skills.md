skills:
  - name: load_dataset
    description: reads CSV, validates columns, reports null count and which rows before returning
    input: File path (string) pointing to a CSV with columns — period, ward, category, budgeted_amount, actual_spend, notes.
    output: Validated dataset (in-memory table/dataframe) plus a pre-flight report listing total rows, null count, and the period·ward·category identity of each null row with its notes reason.
    error_handling: Refuses to proceed if required columns are missing; raises an explicit error listing the missing columns. If the file path is invalid or unreadable, raises a file-not-found error and does not guess an alternative path.

  - name: compute_growth
    description: takes ward + category + growth_type, returns per-period table with formula shown
    input: growth_type (string — must be "MoM" or "YoY"), validated dataset from load_dataset, optional ward(s) (list of strings), optional category(ies) (list of strings).
    output: Table with columns — Ward, Category, Period, Actual Spend (₹ lakh), MoM Growth, Formula, Null Flag.
    error_handling: If growth_type is not "MoM" or "YoY", refuses and asks the user to specify — never defaults silently. If the ward or category filters yield no results, returns a clear error message.
