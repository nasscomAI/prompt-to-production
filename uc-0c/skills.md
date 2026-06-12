skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are present,
      and reports the total null count and the identity of every null actual_spend
      row before returning the dataset for downstream use.
    input:
      type: string
      format: >
        File path to a CSV file containing columns: period (YYYY-MM), ward (string),
        category (string), budgeted_amount (float), actual_spend (float or blank),
        notes (string).
    output:
      type: object
      format: >
        A structured dataset (all rows) plus a null_report list where each entry
        contains period, ward, category, and the null reason sourced from the notes
        column. Null count summary is included as a header field.
    error_handling: >
      If the file path is invalid or the file cannot be read, raise a descriptive
      error and halt. If any required column (period, ward, category, budgeted_amount,
      actual_spend, notes) is missing, list the missing columns and refuse to proceed.
      If actual_spend nulls are present but notes is also null for those rows, flag
      each affected row as "null reason unavailable" rather than silently skipping.
      Never impute, fill, or drop null actual_spend values.

  - name: compute_growth
    description: >
      Takes a single ward, a single category, and an explicit growth type, then
      returns a per-period table of growth figures with the exact formula displayed
      alongside every computed result.
    input:
      type: object
      format: >
        Three required fields — ward (string, must match a value present in the
        dataset), category (string, must match a value present in the dataset),
        growth_type (string, must be one of: "MoM" or "YoY"). All three fields
        are mandatory; no defaults are assumed.
    output:
      type: table
      format: >
        One row per period containing: period (YYYY-MM), actual_spend (float or
        "NULL — <reason from notes>"), prior_period_spend (float or "NULL"),
        formula (string, e.g. "(19.7 - 14.8) / 14.8 × 100"), and
        growth_pct (float or "NOT COMPUTED — null value"). Null rows appear in
        the table flagged, not omitted.
    error_handling: >
      If growth_type is not supplied, refuse to proceed and ask the caller to
      specify MoM or YoY — never guess or default. If ward or category does not
      match any value in the dataset, return an explicit "no matching data" error
      listing the supplied value and the valid options. If the caller requests
      output spanning multiple wards or categories simultaneously without an
      explicit per-ward breakdown instruction, refuse and explain that aggregation
      across wards or categories is not permitted. If the prior period value
      required for growth calculation is itself null, mark the growth result as
      "NOT COMPUTED — prior period null" rather than propagating an incorrect value.
