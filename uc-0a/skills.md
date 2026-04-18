
# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint into category, priority, reason,
      and optional review flag using explicit enforcement rules.
    input: >
      One complaint description as a free-text string.
    output: >
      category (string), priority (string), reason (string),
      flag (string or empty).
    error_handling: >
      If category is ambiguous or unsupported by explicit text evidence,
      return category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: >
      Processes a CSV file of complaint descriptions by applying
      classify_complaint to each row and writing structured results to output.
    input: >
      CSV file with complaint description column.
    output: >
      CSV file with category, priority, reason, and flag columns populated.
    error_handling: >
      If input rows are malformed or missing descriptions,
      skip the row and flag it as NEEDS_REVIEW.
