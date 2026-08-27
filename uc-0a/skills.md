skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into a standardized category and priority with a cited reason.
    input: A dictionary or object representing a single CSV row (must contain a 'description' field).
    output: A dictionary containing 'category' (one of 10 allowed types), 'priority' (Urgent/Standard/Low), 'reason' (one-sentence justification), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: For empty descriptions or unresolvable ambiguity, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a complaint CSV file by applying the classification skill to each row and saving the results.
    input: File paths for the input CSV and the target output CSV.
    output: A Boolean indicating success or a summary of rows processed and saved.
    error_handling: Handles file system errors (file not found, permission denied) and logs individual row failures while ensuring the process completes.
