skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into a structured output with
      category (one of 10 allowed), priority (Urgent/Standard/Low),
      one-sentence reason citing the description, and a flag
      (blank or NEEDS_REVIEW for genuinely ambiguous cases).
    input: >
      dict — a single row from the input CSV, must contain at minimum
      a 'description' field. May optionally contain a 'complaint_id' field.
    output: >
      dict — keys: complaint_id (preserved from input), category (str),
      priority (str), reason (str), flag (str — '' or 'NEEDS_REVIEW').
    error_handling: >
      If the description is empty or missing, raises ValueError.
      If the category is genuinely ambiguous from the description alone,
      sets category to 'Other' and flag to 'NEEDS_REVIEW'
      (never guesses a category).

  - name: batch_classify
    description: >
      Reads an input CSV of complaint rows, applies classify_complaint
      to each row, and writes the results to an output CSV.
    input: >
      str (input_path) — path to CSV with at least a 'description'
      column; str (output_path) — path to write results CSV.
    output: >
      CSV written to output_path with columns:
      complaint_id, category, priority, reason, flag.
      Prints completion message on success.
    error_handling: >
      Skips rows that fail classification (logs warning, leaves them
      out of output). Never crashes on a single bad row.
      Raises FileNotFoundError if input_path does not exist.
