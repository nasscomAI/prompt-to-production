skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description.
    input: A dictionary or object containing the complaint description (string) and any other row data.
    output: A dictionary with keys 'category' (string from allowed list), 'priority' (Urgent/Standard/Low), 'reason' (string sentence), 'flag' (string 'NEEDS_REVIEW' or empty).
    error_handling: If the description is empty or invalid, return category 'Other', priority 'Low', reason 'Invalid input', flag 'NEEDS_REVIEW'. For ambiguous descriptions matching failure modes like taxonomy drift or severity blindness, enforce exact category names, check for severity keywords strictly, and flag if genuinely uncertain.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: File paths for input CSV (string) and output CSV (string).
    output: Writes a CSV file with additional columns for category, priority, reason, flag; returns success status or error message.
    error_handling: If input file does not exist or is malformed, raise an error and do not write output. For rows with missing descriptions, classify as invalid. Ensure all rows are processed, and output matches input row count.
