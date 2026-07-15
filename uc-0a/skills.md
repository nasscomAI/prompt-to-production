skills:
  - name: classify_complaint
    description: >
      Classifies a single civic complaint row into a structured record containing
      category, priority, reason, and flag based solely on the description field.
    input: >
      A dict representing one CSV row with keys: complaint_id, date_raised, city,
      ward, location, description, reported_by, days_open.
      The description field is the primary input; all other fields are passed through
      unchanged to the output.
    output: >
      A dict with keys: complaint_id, category, priority, reason, flag.
      - category: exactly one of the ten allowed strings
      - priority: "Urgent", "Standard", or "Low"
      - reason: one sentence citing specific words from the description
      - flag: "NEEDS_REVIEW" or "" (empty string)
    error_handling: >
      If the description field is missing or empty, set category to "Other",
      priority to "Standard", reason to "Description field is missing or empty —
      cannot classify", and flag to "NEEDS_REVIEW".
      Never raise an exception for a single bad row; log the error and return the
      safe-default dict so batch processing continues.

  - name: batch_classify
    description: >
      Reads an input CSV file of complaint rows, applies classify_complaint to each
      row, and writes a results CSV containing all original fields plus the four
      classification fields.
    input: >
      - input_path: string — absolute or relative path to the input CSV file
        (must have columns: complaint_id, description at minimum)
      - output_path: string — path where the results CSV will be written
    output: >
      A CSV file at output_path containing all original columns plus:
      category, priority, reason, flag.
      Also prints a summary to stdout: total rows processed, Urgent count,
      NEEDS_REVIEW count, and any rows that raised errors.
    error_handling: >
      If the input file does not exist or cannot be parsed as CSV, raise a clear
      FileNotFoundError or ValueError with a human-readable message — do not silently
      produce an empty output.
      If a single row fails classification, write it to the output with
      category="Other", flag="NEEDS_REVIEW", and a reason explaining the failure;
      continue processing remaining rows.
