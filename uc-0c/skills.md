skills:
  - name: load_dataset
    priority: P1
    rice:
      reach: 10
      impact: 3.0
      confidence: 0.90
      effort: 1
      score: 27.00
      why: "Foundation skill for all safe computation; catches schema/null issues early."
    description: "Read the CSV, validate required columns, and report all null actual_spend rows with notes before any growth math."
    input:
      type: object
      fields:
        - input_csv_path: string
    output:
      type: object
      fields:
        - schema_valid: boolean
        - row_count: integer
        - required_columns_present: string[]
        - null_actual_spend_count: integer
        - null_rows: "[{period, ward, category, notes}]"
        - dataframe_handle: object
    error_handling:
      - "Refuse if file is missing/unreadable."
      - "Refuse if required columns are missing."
      - "Do not suppress nulls; always surface full null_rows list."

  - name: compute_growth
    priority: P1
    rice:
      reach: 9
      impact: 2.8
      confidence: 0.92
      effort: 2
      score: 11.59
      why: "Primary business outcome skill; must remain explicit and auditable."
    description: "Compute MoM or YoY growth for one ward+category only and return a per-period table with formula shown in every row."
    input:
      type: object
      fields:
        - dataframe_handle: object
        - ward: string
        - category: string
        - growth_type: "MoM | YoY"
    output:
      type: table
      columns:
        - period
        - ward
        - category
        - actual_spend
        - growth_type
        - growth_percent
        - formula
        - status
        - notes
    formula_templates:
      MoM: "((current - previous_month) / previous_month) * 100"
      YoY: "((current - same_month_last_year) / same_month_last_year) * 100"
    error_handling:
      - "Refuse if growth_type is missing or not MoM/YoY."
      - "Refuse if request implies all-ward or all-category aggregation."
      - "If current or baseline value is null/invalid, set status=FLAGGED_NULL and do not compute growth_percent."
      - "If baseline is zero, set status=NON_COMPUTABLE_DIV_BY_ZERO and do not compute growth_percent."
