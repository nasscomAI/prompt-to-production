# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Takes a single complaint row and returns category, priority, reason, and flag.
    input: >
      A dictionary or CSV row containing at minimum a "description" field (string).
      May also contain metadata fields like ward, date, or source — these are
      ignored for classification.
    output: >
      A dictionary with exactly four keys: category (string, one of the 10 allowed
      values), priority (string: Urgent, Standard, or Low), reason (string, one
      sentence), flag (string: NEEDS_REVIEW or empty string).
    error_handling: >
      If description is missing or empty, return category Other, priority Low,
      reason explaining the emptiness, and flag NEEDS_REVIEW. If description
      contains no classifiable content (e.g. random characters), same fallback
      applies.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: >
      File path to a CSV file (string). The CSV must contain a "description" column.
      Other columns are preserved but not used for classification.
    output: >
      File path to the output CSV (string). The output CSV contains all original
      columns plus four new columns: category, priority, reason, flag. The output
      has the same number of rows as the input.
    error_handling: >
      If the input file does not exist, raise FileNotFoundError. If the input CSV
      has no description column, raise ValueError with a message listing the
      available columns. Rows with missing descriptions are classified with the
      Other/Low/NEEDS_REVIEW fallback.
