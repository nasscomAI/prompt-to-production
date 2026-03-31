skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint description to output a category, priority, reason, and optional review flag.
    input: A single string representing the text of the citizen complaint.
    output: A structured object or dictionary containing exactly four fields - category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: If input is unparseable or cannot be classified, returns category 'Other', flag 'NEEDS_REVIEW', and standard fallback values.

  - name: batch_classify
    description: Iterates through a dataset of complaints in a CSV file, applying classify_complaint to each row, and generating an output CSV.
    input: File paths for a source input CSV (with complaint data) and a destination output CSV.
    output: Successfully writes a results CSV file to disk containing the classifications appended to the row data.
    error_handling: Halts and outputs an error message if the input file does not exist or has an incompatible format.
