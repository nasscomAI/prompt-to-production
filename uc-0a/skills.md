# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Takes a single complaint row (complaint_id + description) and returns
      a structured classification with category, priority, reason, and flag.
    input: >
      A dict with keys:
        - complaint_id (string): Unique identifier for the complaint.
        - description (string): Free-text citizen complaint description.
    output: >
      A dict with keys:
        - complaint_id (string): Passed through unchanged from input.
        - category (string): Exactly one of: Pothole · Flooding · Streetlight ·
          Waste · Noise · Road Damage · Heritage Damage · Heat Hazard ·
          Drain Blockage · Other.
        - priority (string): Exactly one of: Urgent · Standard · Low.
        - reason (string): One sentence citing specific words from description.
        - flag (string): "NEEDS_REVIEW" if ambiguous, otherwise empty string "".
    error_handling: >
      If description is missing, None, or empty string:
        - category → "Other"
        - priority → "Low"
        - reason → "No description provided"
        - flag → "NEEDS_REVIEW"
      If description is present but category cannot be determined:
        - category → "Other"
        - flag → "NEEDS_REVIEW"
        - reason must explain the ambiguity using words from the description.
      Never raise an exception for a single row — always return a valid dict.

  - name: batch_classify
    description: >
      Reads an input CSV file, applies classify_complaint to every row,
      and writes a results CSV with all classification outputs. Continues
      processing even if individual rows fail.
    input: >
      Two file path strings:
        - input_path (string): Path to the CSV file with columns including
          complaint_id and description. The category and priority_flag
          columns are stripped — do not expect them.
        - output_path (string): Path where the results CSV will be written.
    output: >
      A CSV file written to output_path with columns:
        complaint_id, category, priority, reason, flag.
      Also prints a summary to stdout:
        - Total rows processed
        - Number of NEEDS_REVIEW flags
        - Number of Urgent rows
        - Any rows that were skipped due to missing data.
    error_handling: >
      If input_path does not exist: print a clear error and exit with code 1.
      If a row is missing complaint_id or description: classify with available
      fields, set flag to NEEDS_REVIEW, and log the row index to stdout.
      If output directory does not exist: attempt to create it, or exit with
      a clear message if creation fails.
      Never crash silently — all errors must be printed before exiting.
