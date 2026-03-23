skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority level, justification, and whether it requires manual review.
    input: A string or dictionary containing the text description of a citizen complaint.
    output: A dictionary with four keys: 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string or blank).
    error_handling: If the input is empty or incomprehensible, return 'category': 'Other', 'priority': 'Low', 'reason': 'Input was unreadable or empty.', 'flag': 'NEEDS_REVIEW'. If the complaint is ambiguous, return 'category': 'Other', 'flag': 'NEEDS_REVIEW' with an appropriate reason.

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV file, applies the classifier to each row, and writes the results to an output CSV file.
    input: Two strings representing file paths: 'input_path' (path to the input CSV file) and 'output_path' (path to write the output CSV file).
    output: A boolean or status object indicating successful completion of the batch processing. The primary side-effect is the creation of the output CSV file.
    error_handling: Keep processing remaining rows if an error occurs on a single row. For failed rows, write a row with 'category': 'Other', 'flag': 'ERROR_PROCESSING', and log the error. Do not crash the entire batch process due to bad rows. Handle missing or unreadable input files by throwing a clear filesystem error.
