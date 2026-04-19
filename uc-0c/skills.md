skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its schema, and reports null actual_spend rows before analysis.
    input:
      type: file
      format: CSV file path containing `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, and `notes` columns.
    output:
      type: object
      format: >
        Structured dataset with validated rows, discovered ward and category
        values, and a list of null-actual-spend rows including period, ward,
        category, and notes.
    error_handling: >
      If the file is missing, unreadable, or lacks any required column, abort
      with a clear error. If numeric fields are malformed, abort and identify
      the row. Blank `actual_spend` must be preserved as null and reported; do
      not coerce blanks to zero or skip them silently.

  - name: compute_growth
    description: Computes a per-period growth table for one ward and one category using the explicitly requested growth type.
    input:
      type: object
      format: >
        Validated dataset plus `ward` (string), `category` (string), and
        `growth_type` (string, expected `MoM` for this use case).
    output:
      type: file_content
      format: >
        CSV-ready per-period table containing period, ward, category,
        actual_spend, growth_type, formula, growth_percent, status, and details.
    error_handling: >
      If `ward`, `category`, or `growth_type` is missing, invalid, or ambiguous,
      refuse instead of guessing. If the request implies all-ward or all-category
      aggregation, refuse. If the current or previous period needed for
      computation has null `actual_spend`, mark the row as flagged and explain
      why instead of computing a value. Never choose a formula silently and never
      aggregate beyond the requested ward-category scope.
