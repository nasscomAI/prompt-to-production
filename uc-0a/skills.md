# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint row in and returns category + priority + reason + flag out.
    input: One complaint row containing the citizen complaint description.
    output: category, priority, reason, flag
    error_handling: Refusal condition - if genuinely ambiguous, refuse rather than guess (set category to Other, flag to NEEDS_REVIEW).

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: Input CSV file path.
    output: Output CSV file.
    error_handling: Handle file missing errors and catch row-level parsing failures.
