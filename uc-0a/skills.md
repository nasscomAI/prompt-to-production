# skills.md

skills:
  - name: classify_complaint
    description: >
      Classify one citizen complaint into the permitted category and priority,
      provide a source-grounded reason, and flag genuine ambiguity.
    input: >
      A dictionary representing one complaint CSV row, including its complaint
      identifier and complaint description.
    output: >
      A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: >
      If the complaint description is missing or invalid, return category Other,
      priority Standard, a reason stating that the description is unavailable,
      and flag NEEDS_REVIEW. Never invent missing information.

  - name: batch_classify
    description: >
      Read a complaint CSV, apply classify_complaint to every row, and write
      the resulting classifications to an output CSV.
    input: >
      An input CSV path and an output CSV path.
    output: >
      A CSV containing complaint_id, category, priority, reason, and flag for
      every input row.
    error_handling: >
      Process rows independently so one malformed row does not stop the batch.
      Invalid or ambiguous rows must still appear in the output and be flagged
      for review where appropriate.
