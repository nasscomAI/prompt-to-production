skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority, reason, and an ambiguity flag.
    input: Single row containing the complaint description (string)
    output: Data structure containing category, priority, reason, and flag
    error_handling: If input mapping is highly uncertain or fails, assign category "Other", assign flag "NEEDS_REVIEW", and state the ambiguity in reason.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Input CSV path (string)
    output: Output CSV path (string)
    error_handling: Log any row-level processing errors and write a fallback row using the "NEEDS_REVIEW" flag so the batch execution can complete without failing entirely.
