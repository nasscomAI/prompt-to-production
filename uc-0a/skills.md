skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority, reason, and review flag.
    input: A string containing the citizen complaint description.
    output: A structured record containing category (string), priority (string), reason (string), and flag (string).
    error_handling: Return category 'Other', priority 'Standard', no reason, and flag 'NEEDS_REVIEW' if the input format is invalid or missing.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV.
    output: File path to the newly generated output CSV containing classifications.
    error_handling: Log errors for malformed rows and flag them as NEEDS_REVIEW, continuing with the rest of the file. Halts execution if the file cannot be read or written.
