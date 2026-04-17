skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to assign a category and priority level while providing a cited reason.
    input: Dictionary object representing a single row from the citizen complaint data (specifically the description text).
    output: A dictionary containing the classified 'category', 'priority', 'reason', and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Assigns category 'Other' and sets the flag to 'NEEDS_REVIEW' if the description is missing or ambiguous.

  - name: batch_classify
    description: Manages the CSV processing pipeline, reading raw complaint data and writing the finalized classifications to a result file.
    input: File paths for the source CSV (input) and the destination results file (output).
    output: Success confirmation and a summary of processed complaints.
    error_handling: Validates file existence and permissions; logs row-level failures to ensure the entire batch isn't halted by one error.
