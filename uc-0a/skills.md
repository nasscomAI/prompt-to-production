skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description to determine its category, priority, reason, and flag.
    input: A single text string or row containing a citizen complaint description.
    output: A structured record containing exactly four fields (category, priority, reason, flag).
    error_handling: If the input is unclassifiable or genuinely ambiguous, assign category as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill to each row, and writes the classification results to an output CSV file.
    input: A file path string to an input CSV containing citizen complaints.
    output: A file path string to an output CSV where the classification results will be saved.
    error_handling: If the input file is missing or cannot be read, halt execution and raise an error.
