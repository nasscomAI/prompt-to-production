# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Maps one citizen complaint row to an exact category, a priority level, a
      one-sentence reason citing description words, and an ambiguity flag.
    input: >
      One dict per CSV row containing complaint_id (str) and description (str),
      plus optional metadata fields such as ward and location.
    output: >
      dict with keys complaint_id, category, priority, reason, flag where
      category is one of the 10 allowed values and priority is Urgent or Standard.
    error_handling: >
      Empty or missing description returns category Other, priority Standard,
      reason explaining the missing text, and flag NEEDS_REVIEW. When several
      category rules match, the closest category is returned with flag
      NEEDS_REVIEW. Severity keywords always force priority Urgent.

  - name: batch_classify
    description: >
      Reads a complaint CSV, applies classify_complaint to every row, and writes
      the classified results to an output CSV.
    input: >
      Input CSV file path and output CSV file path (strings).
    output: >
      CSV file with headers complaint_id, category, priority, reason, flag —
      one result row per input row.
    error_handling: >
      Missing or unreadable input raises FileNotFoundError. Individual malformed
      rows are written as category Other with flag NEEDS_REVIEW instead of
      stopping the batch. Files are read with utf-8-sig so the BOM and unicode
      dashes in city data are preserved.