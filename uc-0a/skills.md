skills:
  - name: classify_complaint
    description: Processes a single complaint description and returns its classification fields.
    input: A text string containing the citizen's complaint description.
    output: A structured object with four fields - category (string), priority (string), reason (string), and flag (string or blank).
    error_handling: If the text is genuinely ambiguous or lacks enough detail to categorize, flag should be set to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaint rows, processes each row using classify_complaint, and writes the structured results to an output CSV.
    input: File paths for the input CSV and the output CSV.
    output: A new CSV file saved to the output path containing the classified results (category, priority, reason, flag) for each row.
    error_handling: If a row cannot be processed due to a formatting error, log the error and continue to the next row to ensure the entire batch completes.
