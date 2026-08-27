# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into a structured output with category, priority, reason, and flag.
    input: A plain-text complaint description string from one CSV row.
    output: "A dict with four fields — category (str, one of the 10 allowed values), priority (str: Urgent | Standard | Low), reason (str, one sentence quoting words from the description), flag (str: NEEDS_REVIEW or blank)."
    error_handling: If the description is empty or unparseable, output category as Other, priority as Low, reason as "Description could not be interpreted", and flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: "Path to input CSV file (str) containing at least a description column; path to output CSV file (str)."
    output: Output CSV file written to the specified path, with all original columns preserved and four new columns appended — category, priority, reason, flag.
    error_handling: If a row is missing the description field, classify_complaint is called with an empty string and the row is still written to output. File-level errors (missing input file, write permission denied) raise an exception with a clear message and halt processing.
