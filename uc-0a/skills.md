skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description, returning its category, priority, reason, and a potential review flag.
    input: String (A single citizen complaint description text).
    output: Dictionary containing `category`, `priority`, `reason`, and `flag` fields formatted exactly per rules.
    error_handling: If the description is genuinely ambiguous, return category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: File path (Location of the input CSV file containing unclassified complaint rows).
    output: File path (Location where the fully categorized CSV file will be saved).
    error_handling: Skip malformed rows, log the error, and continue processing the remaining rows in the batch without halting entirely.
