skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a specific category, assigns a priority level, and provides a reason with an optional review flag.
    input: One complaint row containing the text description (String).
    output: A classified record containing category (String), priority (String), reason (String), and flag (String) fields.
    error_handling: If the text is genuinely ambiguous and cannot be confidently classified, defaults category to Other and sets the flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Processes a batch of citizen complaints by reading an input CSV, applying the classify_complaint skill to each row, and generating an output CSV.
    input: Path to an input CSV file containing raw complaint descriptions (String).
    output: Path to an output CSV file containing the classification results (String).
    error_handling: Logs any failures or unparseable rows and continues processing the rest of the batch, ensuring the script completes execution.
