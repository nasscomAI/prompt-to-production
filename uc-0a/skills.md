skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint row and determines its proper category, priority, justification reason, and review flag.
    input: A single complaint text description (string).
    output: A structured record containing category, priority, reason, and flag fields.
    error_handling: If the input is unreadable or ambiguous, sets category to 'Other' and flags with 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of citizen complaints from an input CSV, processes each using classify_complaint, and writes the structured results to an output CSV.
    input: File path to the input CSV containing complaint rows.
    output: File path to the destination output CSV.
    error_handling: If a row is malformed, skips the row, logs a warning, and continues classification for the rest of the batch.
