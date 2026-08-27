skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into a structured dictionary containing category, priority, reason, and flag.
    input:
      type: dict
      format: CSV row dictionary with keys including description, location, etc.
    output:
      type: dict
      format: Keys: complaint_id, category, priority, reason, flag
    error_handling: >
      If description is missing or empty, assign category 'Other', priority 'Standard', flag 'NEEDS_REVIEW', and set reason to 'Missing complaint description.'
      If the category is ambiguous or overlaps between multiple definitions, assign category 'Other' or the closest match, and set the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Process an input CSV file of citizen complaints, classify each row, and write the structured results to an output CSV file.
    input:
      type: string
      format: File paths for input and output CSV files
    output:
      type: string
      format: Confirmation message of written results
    error_handling: >
      If input file does not exist, raise FileNotFoundError.
      If a row contains malformed data or missing columns, flag the row, record the failure, and continue processing remaining rows without crashing.
