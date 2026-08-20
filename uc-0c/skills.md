skills:
  - name: load_dataset
    description: >
      Loads ward budget CSV, validates required schema, and returns typed rows
      with a null-inventory report before any growth computation begins.
    purpose: >
      Prevent silent null handling and schema drift by enforcing input
      integrity and surfacing all null actual_spend rows with source notes.
    input:
      type: object
      required_fields:
        - input_path
      constraints:
        - input_path must point to a readable CSV.
    output:
      type: object
      required_fields:
        - rows
        - schema_validation
        - null_report
      schema_validation:
        required_columns:
          - period
          - ward
          - category
          - budgeted_amount
          - actual_spend
          - notes
      null_report:
        fields:
          - null_count
          - null_rows
        null_rows_schema:
          - period
          - ward
          - category
          - notes
    processing_contract:
      - Validate all required columns before row parsing.
      - Parse numeric columns where present and preserve blank actual_spend as null.
      - Produce deterministic null report including row identity and notes.
      - Reject malformed period values outside YYYY-MM format.
    error_handling:
      file_errors:
        - Raise explicit error if file missing/unreadable.
      schema_errors:
        - Raise explicit error listing missing required columns.
      parse_errors:
        - Raise explicit error for invalid numeric types in budgeted_amount.

  - name: compute_growth
    description: >
      Computes period-wise growth for one ward+category using explicit growth
      type and returns formula-transparent rows with null-safe flags.
    purpose: >
      Prevent wrong aggregation level and formula assumptions by requiring
      explicit scope and explicit growth_type.
    input:
      type: object
      required_fields:
        - rows
        - ward
        - category
        - growth_type
      constraints:
        - ward must match exactly one ward value in dataset.
        - category must match exactly one category value in dataset.
        - growth_type must be one of: MoM, YoY.
    output:
      type: table
      required_columns:
        - period
        - ward
        - category
        - actual_spend
        - growth_type
        - formula
        - growth_percent
        - status
        - reason
      status_allowed:
        - COMPUTED
        - NOT_COMPUTED
    computation_rules:
      mom:
        - Use immediate previous period for same ward+category.
        - Formula text must be included for every row.
      yoy:
        - Use same month previous year for same ward+category when available.
        - If no prior-year comparator exists in dataset range, mark NOT_COMPUTED.
      null_behavior:
        - If current or comparator actual_spend is null, mark NOT_COMPUTED.
        - Include notes-derived reason for null current row where available.
      denominator_behavior:
        - If comparator value is zero, mark NOT_COMPUTED and explain denominator zero.
    enforcement_guards:
      - Refuse all-ward or all-category aggregate requests in this skill.
      - Refuse missing growth_type; never default silently.
      - Never collapse per-period output into a single summary number.
    error_handling:
      validation_errors:
        - Return actionable errors for unknown ward/category/growth_type.
      empty_scope_errors:
        - Return error when no rows exist for requested ward+category.
      compute_errors:
        - Continue row-wise with NOT_COMPUTED where possible; do not crash whole output.
