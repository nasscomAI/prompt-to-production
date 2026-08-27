skills:
  - name: classify_complaint
    description: Processes a single complaint row to assign appropriate classification category and priority.
    input: One complaint description string.
    output: A structured result containing category (string), priority (string), reason (string, one sentence), and flag (string or blank).
    error_handling: If the complaint cannot be confidently categorized, defaults the category to "Other" and sets the flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads complaints from an input CSV, processes each row using classify_complaint, and writes results to an output CSV.
    input: Path to the input CSV file containing unclassified complaints.
    output: Path to the written output CSV file containing the classifications appended to the data.
    error_handling: If an individual row fails processing entirely, flags the row with "NEEDS_REVIEW" and continues to process remaining rows to ensure file creation.
