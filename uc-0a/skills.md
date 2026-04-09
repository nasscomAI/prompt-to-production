# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint record and applies strict categorization and severity rules based on text keyword matching to determine the appropriate response routing.
    input: A single complaint row (dictionary or JSON object) containing at minimum a 'description' field.
    output: A data structure (dictionary or JSON object) containing the 'category', 'priority', 'reason', and 'flag' fields.
    error_handling: If the description is empty, missing, or utterly incomprehensible, fallback to category 'Other', priority 'Standard', reason 'Missing or invalid description', and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Opens an input CSV file containing multiple citizen complaints, iterates through each row applying the classify_complaint skill, and writes all the processed results to an output CSV file.
    input: Two file paths as strings: 'input_csv_path' and 'output_csv_path'.
    output: A newly written CSV file containing the classifications mapped to their respective complaint_ids.
    error_handling: Must silently catch row-level processing errors (e.g., malformed lines) so as not to crash the entire batch job. Rows that crash should be logged and flagged in the output CSV with a 'FAILED' status. Must handle file not found exceptions gracefully.
