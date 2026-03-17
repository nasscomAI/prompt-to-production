# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag fields.
    input: A dictionary or row object containing at minimum a 'description' field with the complaint text (string).
    output: A dictionary with four keys - 'category' (string from allowed list), 'priority' (Urgent/Standard/Low), 'reason' (one sentence string citing words from description), 'flag' (NEEDS_REVIEW or empty string).
    error_handling: If description field is missing or empty, returns category='Other', priority='Standard', reason='No description provided', flag='NEEDS_REVIEW'. If description is ambiguous and does not clearly match any category, returns category='Other' with flag='NEEDS_REVIEW' and reason explaining the ambiguity.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes results to output CSV.
    input: Two file paths (strings) - input_path pointing to CSV with complaint descriptions, output_path for results file.
    output: Writes a CSV file to output_path with original columns plus 'category', 'priority', 'reason', and 'flag' columns. Returns row count (integer) of processed complaints.
    error_handling: If input file does not exist or is not readable, raises FileNotFoundError with clear message. If input CSV is malformed or missing required columns, raises ValueError with details. If output path is not writable, raises PermissionError. All rows are processed even if individual classifications are ambiguous (using flag field to mark them).
