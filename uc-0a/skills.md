# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row by category, priority, reason, and ambiguity flag.
    input: A single complaint record with fields including description text. Type CSV row or dict.
    output: A dict with keys category (string), priority (Urgent/Standard/Low), reason (one-sentence string), flag (NEEDS_REVIEW or empty string).
    error_handling: If category cannot be determined from description alone, set category to Other and flag to NEEDS_REVIEW. If description is empty or unintelligible, set category to Other, priority to Standard, reason to "Insufficient description to classify", and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Read a CSV file of complaints, classify each row using classify_complaint, and write the results to an output CSV.
    input: Path to input CSV file with complaint records; path to output CSV file.
    output: Output CSV file with original columns plus category, priority, reason, and flag columns.
    error_handling: If input file is missing or malformed, raise an error with file path. Skip rows with missing description field and log the row number. If output directory does not exist, create it.
