skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into predefined constraint fields.
    input: A string containing the textual description of a single citizen complaint.
    output: A structured record containing the fields category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: If the input is empty or incomprehensible, return category as 'Other', priority as 'Low', and flag as 'NEEDS_REVIEW'. If ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a batch of citizen complaints from an input CSV, applying the classify_complaint skill to each row, and writes out the results.
    input: A file path to an input CSV where each row has a complaint description.
    output: A file path to an output CSV containing the parsed data with appended category, priority, reason, and flag fields.
    error_handling: If a row fails to process, log the error for that row, default it to 'Other' with flag 'NEEDS_REVIEW', and continue processing the remaining rows. If the input file is unreadable, halt with a file access error.
