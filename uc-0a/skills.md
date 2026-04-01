skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a strict schema including category, priority, reason, and an optional review flag.
    input: A single string or dictionary containing a citizen complaint description.
    output: A structured object containing the exact 'category', 'priority', 'reason', and 'flag'.
    error_handling: Output category as 'Other', flag as 'NEEDS_REVIEW', priority as 'Standard', and explain the ambiguity in the reason field if the input is vague or ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of multiple citizen complaints, calls classify_complaint for each row, and outputs a completed CSV.
    input: File path to a CSV containing rows of citizen complaints.
    output: Output CSV file written to specified path with added classification columns.
    error_handling: Skip malformed rows, log parsing errors without halting the entire process, and proceed with valid rows.
