skills:
  - name: classify_complaint
    description: Classifies one complaint row into schema-compliant category, priority, reason, and flag.
    input: One complaint record containing a free-text description string.
    output: A record with category, priority, reason, and flag using only allowed values.
    error_handling: If description is missing/empty, return category Other, priority Standard, reason "Description missing; unable to classify reliably.", and flag NEEDS_REVIEW. If ambiguous, use category Other and flag NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint row-by-row, and writes a result CSV.
    input: CSV path ../data/city-test-files/test_hyderabad.csv with complaint rows where category and priority columns are absent.
    output: CSV path uc-0a/results_hyderabad.csv where each row includes category, priority, reason, and flag.
    error_handling: If input file is unreadable, malformed, or required complaint text is absent in a row, preserve row order and mark affected rows as NEEDS_REVIEW with a reason explaining the issue.
