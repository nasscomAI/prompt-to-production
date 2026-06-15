# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates the required schema, converts
      numeric fields, and reports all null actual_spend rows before returning.
    input: >
      CSV file path containing period, ward, category, budgeted_amount,
      actual_spend, and notes columns.
    output: >
      List of row records with typed budgeted_amount and actual_spend values,
      plus a pre-computation report of the null count and each null row's
      period, ward, category, and notes reason.
    error_handling: >
      Refuse invalid or missing files, missing required columns, and malformed
      numeric values. Treat blank actual_spend as null and preserve notes as
      the reason.

  - name: compute_growth
    description: >
      Computes growth for one explicit ward/category slice using the requested
      growth_type and emits formula text for each period.
    input: >
      Validated dataset rows, exact ward string, exact category string, and
      explicit growth_type such as MoM or YoY.
    output: >
      Per-period table with ward, category, period, actual spend, comparison
      period, comparison spend, growth type, growth percentage when computable,
      formula, status, and null/error reason when not computable.
    error_handling: >
      Refuse missing ward, missing category, missing growth_type, unsupported
      growth_type, empty ward/category matches, null current or comparison
      actual_spend, missing comparison periods, and division by zero. Never
      aggregate across wards or categories to compensate for missing inputs.
