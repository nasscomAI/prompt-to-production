# skills.md

skills:
  - name: classify_complaint
    description: one complaint row in → category + priority + reason + flag out
    input: one complaint row
    output: category + priority + reason + flag
    error_handling: Set flag to NEEDS_REVIEW when category is genuinely ambiguous

  - name: batch_classify
    description: reads input CSV, applies classify_complaint per row, writes output CSV
    input: input CSV path
    output: output CSV path
    error_handling: flag nulls, do not crash on bad rows, produce output even if some rows fail
