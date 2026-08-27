skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: dictionary with complaint_id and description
    output: dictionary with classification fields
    error_handling: If unclear → category Other + NEEDS_REVIEW

  - name: batch_classify
    description: Reads CSV and classifies all rows
    input: input CSV path and output CSV path
    output: CSV file with results
    error_handling: Handles bad rows safely without crashing