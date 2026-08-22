# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into standardized category, priority, reason, and review flag.
    input: A dictionary containing a complaint description text field.
    output: A dictionary with four fields: category (one of 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing specific words), flag (NEEDS_REVIEW or blank).
    error_handling: If description is empty or cannot be classified, return category "Other" with flag "NEEDS_REVIEW" and reason explaining the ambiguity.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes results to an output CSV file.
    input: Input CSV file path with complaint descriptions.
    output: Output CSV file path with classification results added.
    error_handling: If input file is missing or malformed, raise descriptive error. Process all valid rows and skip invalid ones with warnings.