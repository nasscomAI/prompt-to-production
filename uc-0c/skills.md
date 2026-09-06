# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its columns, and reports nulls before any
      computation.
    input: >
      Path to a CSV with columns: period, ward, category, budgeted_amount,
      actual_spend, notes.
    output: >
      The dataset as parsed rows, plus a validation summary: column list confirmed,
      null count, and the rows (period/ward/category) where actual_spend is null
      together with their notes reason.
    error_handling: >
      Refuses to proceed (raises a clear error) if a required column is missing;
      always surfaces the null rows and their notes before returning.

  - name: compute_growth
    description: >
      Computes growth for one ward + one category and returns a per-period table with
      the formula shown.
    input: >
      The validated dataset, a ward string, a category string, and a growth type
      (MoM or YoY) explicitly supplied.
    output: >
      A per-period table (one row per period in scope) with columns: period,
      budgeted_amount, actual_spend, growth value, formula used.
    error_handling: >
      Refuses if growth type is missing (asks, never guesses); refuses if the request
      spans all wards or all categories without explicit instruction; flags null
      periods with their notes reason and does not compute a value for them.