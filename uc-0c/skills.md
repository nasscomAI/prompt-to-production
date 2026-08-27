skills:

  - name: load_dataset
    description: >
      Load and validate the municipal budget CSV. Perform mandatory schema validation
      and detect all null actual_spend rows BEFORE any downstream computation.

    input:
      - file_path: string

    output:
      data:
        - full dataset (DataFrame)
      metadata:
        - total_rows (expected: 300)
        - null_count (expected: 5)
        - null_rows:
            - period
            - ward
            - category
            - notes

    validation:
      required_columns:
        - period
        - ward
        - category
        - budgeted_amount
        - actual_spend
        - notes

    error_handling:
      - condition: file_not_found
        action: raise_error("Input file not found")

      - condition: missing_columns
        action: raise_error("Dataset schema invalid: required columns missing")

    constraints:
      - "Must detect and report ALL null actual_spend rows before returning"
      - "Must not modify, impute, or drop null values"
      - "Must return null row details including notes (reason)"
      - "Must not perform any aggregation or filtering"

  - name: compute_growth
    description: >
      Compute per-period growth (e.g., MoM) for a SINGLE ward and SINGLE category.
      Must enforce strict scope, null handling, and explicit formula reporting.

    input:
      - ward: string (exact match, single value)
      - category: string (exact match, single value)
      - growth_type: string (required; e.g., MoM or YoY)
      - dataset: DataFrame (output of load_dataset)

    output:
      file: uc-0c/growth_output.csv
      columns:
        - period
        - ward
        - category
        - actual_spend
        - growth_percentage
        - formula_used
        - notes

    processing_rules:
      - "Filter dataset to EXACTLY one ward AND one category"
      - "Expected result after filtering: 12 rows (Jan–Dec 2024)"
      - "Sort by period ascending before computation"

      - first_row_rule:
          - growth_percentage = NULL
          - formula_used = "No previous period"

      - growth_logic:
          MoM: "((current_actual - previous_actual) / previous_actual) * 100"
          YoY: "((current_actual - previous_year_actual) / previous_year_actual) * 100"

      - null_handling:
          condition: current_actual IS NULL OR previous_actual IS NULL
          action:
            - growth_percentage = NULL
            - formula_used = "Not computed due to null input"
            - preserve notes column

      - formula_requirement:
          - "Each computed row must include the exact numeric formula used"
          - example: "((19.7 - 14.8) / 14.8) * 100"

    error_handling:
      - condition: ward_not_found
        action: raise_error("Specified ward not found")

      - condition: category_not_found
        action: raise_error("Specified category not found")

      - condition: multiple_wards_detected
        action: raise_error("Aggregation across wards is not allowed")

      - condition: multiple_categories_detected
        action: raise_error("Aggregation across categories is not allowed")

      - condition: missing_growth_type
        action: raise_error("growth_type must be specified")

      - condition: invalid_growth_type
        action: raise_error("Unsupported growth_type; must be MoM or YoY")

      - condition: filtered_row_count_not_12
        action: raise_error("Unexpected data scope — possible aggregation or missing data")

    constraints:
      - "Never aggregate across wards or categories"
      - "Must operate on exactly one ward and one category"
      - "Must not compute growth if null values are involved"
      - "Must include formula_used in EVERY row"
      - "Must output exactly 12 rows (one per month)"
      - "Must preserve null rows in output (no dropping)"