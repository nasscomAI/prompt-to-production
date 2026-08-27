
skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category and priority level.
    input: A single complaint text/row (string or dict).
    output: Dictionary containing `category`, `priority`, `reason` (citing specific text), and `flag` (blank or 'NEEDS_REVIEW' if ambiguous).
    error_handling: If the complaint cannot be matched or is highly ambiguous, sets `flag` to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, runs classify_complaint on each, and saves a resulting CSV.
    input: Input CSV path (string) and output CSV path (string).
    output: CSV file saved to the output path containing the processed rows.
    error_handling: Fails gracefully if input CSV is missing. Handles badly formatted rows by skipping or marking them.
