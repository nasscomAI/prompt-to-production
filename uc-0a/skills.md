skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and review flag.
    input: Complaint description text (string) from one row of the CSV file.
    output: category (string), priority (string), reason (string), flag (string or blank).
    error_handling: If the complaint cannot be mapped to a known category, return category "Other" and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input CSV file, applies classify_complaint to each complaint, and writes results to an output CSV file.
    input: CSV file path containing complaint descriptions.
    output: CSV file with added columns category, priority, reason, and flag.
    error_handling: If the file is missing or malformed, stop execution and print an error message.