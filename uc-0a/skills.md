# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and optional review flag.
    input: String (complaint description text from a single row).
    output: Dictionary with keys category, priority, reason, flag. Category is one of the 10 allowed values or Other. Priority is Urgent, Standard, or Low. Reason is one sentence citing specific words. Flag is NEEDS_REVIEW or empty string.
    error_handling: If category cannot be determined from the description alone, output category=Other and flag=NEEDS_REVIEW. If description is empty or unintelligible, output category=Other, reason="Unable to classify from description", flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads all rows from an input CSV, applies classify_complaint to each, and writes results to output CSV with the same schema.
    input: File path to input CSV with column "description". Must exist and be readable.
    output: File path to output CSV with columns category, priority, reason, flag. One row per input row, in the same order.
    error_handling: If input file does not exist or is malformed, raise clear error with file path. If any row fails classification, log the row number and description, output category=Other and flag=NEEDS_REVIEW for that row, and continue processing remaining rows. Write full output file even if some rows required NEEDS_REVIEW.
