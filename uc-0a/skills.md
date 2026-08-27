# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into schema-constrained category, priority, reason, and flag outputs.
    input: >
      One complaint record (dict/object) with free-text description and optional
      metadata columns from the input CSV.
    output: >
      One normalized record with category, priority, reason, and flag, where
      category and priority are exact allowed strings.
    error_handling: >
      If description is empty or non-informative, return category=Other,
      priority=Standard, reason indicating insufficient detail, and
      flag=NEEDS_REVIEW. If category is ambiguous, return best-safe category=Other
      with flag=NEEDS_REVIEW. Never emit out-of-schema labels.

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint row-by-row, and writes a schema-valid output CSV.
    input: >
      Input CSV path (with complaint rows missing category and priority/priority_flag)
      and output CSV path.
    output: >
      Output CSV containing all input rows plus filled category, priority, reason,
      and flag columns for every row.
    error_handling: >
      Fail fast on unreadable file paths or malformed CSV structure with a clear
      message. For row-level ambiguities, continue processing and mark affected
      rows with flag=NEEDS_REVIEW instead of stopping the batch.
