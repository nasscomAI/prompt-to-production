skills:
  - name: load_dataset
    description: >
      Reads the ward-budget CSV, validates its required fields, and returns
      source rows together with a complete inventory of null actual-spend rows.
    input: >
      A path to a CSV containing period, ward, category, budgeted_amount,
      actual_spend, and notes columns.
    output: >
      Structured rows in source order plus a null report listing the period,
      ward, category, and notes for every blank actual_spend value, and the
      total null count.
    error_handling: >
      Clearly reject a missing, unreadable, empty, or malformed file and any
      missing required column. Do not substitute values for missing actual_spend;
      retain each null row and its note for downstream computation.

  - name: compute_growth
    description: >
      Calculates a per-period growth table for one requested ward and category
      using an explicit, supported growth method.
    input: >
      Validated dataset rows; one exact ward; one exact category; and an explicit
      growth_type such as MoM. For MoM, periods must be sorted chronologically.
    output: >
      A per-period table limited to the requested ward and category, including
      period, actual spend, growth result or flagged non-computation, formula,
      and source null note where applicable.
    error_handling: >
      Refuse missing or unsupported growth_type and requests that aggregate
      multiple wards or categories. Flag rather than compute rows with a null or
      unavailable comparison value, a zero denominator, or a gap in the required
      period sequence; never treat these conditions as zero growth.
