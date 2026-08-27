skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag fields.
    input:
      type: dict
      format: A dictionary containing complaint_id and description fields from one CSV row.
    output:
      type: dict
      format: A dictionary with keys category (string), priority (string), reason (string), and flag (string).
    error_handling: If description is empty or missing, return category Other, priority Low, reason No description provided, and flag NEEDS_REVIEW. If category is genuinely ambiguous, return category Other and flag NEEDS_REVIEW. Never hallucinate sub-categories or variations not in the allowed list.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes results to an output CSV.
    input:
      type: file path
      format: Path to input CSV file containing complaint_id and description columns (category and priority_flag columns are stripped).
    output:
      type: file path
      format: Path to output CSV file containing all input columns plus category, priority, reason, and flag columns.
    error_handling: If input file does not exist or is not a valid CSV, raise FileNotFoundError with message. If input CSV has no rows, create output CSV with headers only. If classify_complaint returns invalid output for a row, log the error and continue processing remaining rows, writing NEEDS_REVIEW flag for that row.