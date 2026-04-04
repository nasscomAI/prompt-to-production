# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag according to the RICE-enforced rules.
    input: |
      Dictionary with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
      (Only 'complaint_id' and 'description' are used for classification; others are ignored.)
    output: |
      Dictionary with keys:
        - complaint_id (string): from input
        - category (string): one of the allowed categories
        - priority (string): Urgent, Standard, or Low
        - reason (string): single sentence citing specific words from description
        - flag (string): "NEEDS_REVIEW" or blank
    error_handling: |
      If description is empty or null, output category="Other", priority="Standard", reason="No description provided", flag="NEEDS_REVIEW".
      If description is too ambiguous to classify (cannot confidently choose a category), output the best guess, set flag="NEEDS_REVIEW", and cite ambiguity in reason.

  - name: batch_classify
    description: Read input CSV file, classify each complaint row using classify_complaint, and write results to output CSV file.
    input: |
      Path to input CSV file with headers: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: |
      Path to output CSV file with headers: complaint_id, category, priority, reason, flag
      File created at the specified output path.
    error_handling: |
      On bad/missing rows in input, log a warning, set category="Other", reason="Row processing failed", flag="NEEDS_REVIEW", and continue processing.
      Never crash; ensure all rows produce output even if some fail.
      Write all successfully processed rows to the output file regardless of errors on individual rows.
