# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category and priority level with a supporting reason.
    input: A dictionary or object representing a single CSV row, containing at least a 'description' field.
    output: A structured object containing 'category' (string), 'priority' (Urgent/Standard/Low), 'reason' (one sentence citing description), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If category is ambiguous, sets category to 'Other' and flag to 'NEEDS_REVIEW'. If description is missing, returns default 'Other'/'Low' values with a 'MISSING_DATA' flag.

  - name: batch_classify
    description: Manages the end-to-end processing of a batch of complaints from an input CSV to a structured output CSV.
    input: File paths for the input CSV (containing citizen complaints) and the desired output CSV destination.
    output: A CSV file at the specified output path containing all classified fields for each input row.
    error_handling: Validates existence of input file and CSV column headers; logs errors for malformed rows while continuing to process valid ones.
