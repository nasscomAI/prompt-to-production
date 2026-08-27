skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and review flag.
    input: A string representing the complaint description.
    output: A dictionary/object with keys 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: If input is empty, null, or invalid, sets category to 'Other', priority to 'Standard', reason to 'Empty or invalid input.', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Two strings representing the input file path (CSV) and the output file path (CSV).
    output: A boolean indicating success or None. Creates a CSV file with classified complaint rows.
    error_handling: If the input file is not found, raises an exception or logs an error. If individual row classification fails, sets default values for that row and marks it with 'NEEDS_REVIEW' flag.
