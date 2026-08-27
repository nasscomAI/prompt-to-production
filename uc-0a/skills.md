# skills.md

skills:
  - name: classify_complaint
    description: one complaint row in → category + priority + reason + flag out
    input: one complaint row in
    output: category + priority + reason + flag out
    error_handling: Set flag to NEEDS_REVIEW when category is genuinely ambiguous

  - name: batch_classify
    description: reads input CSV, applies classify_complaint per row, writes output CSV
    input: input CSV
    output: output CSV
    error_handling: Halt execution if file is missing, or skip invalid rows
