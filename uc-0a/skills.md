# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint row into category, priority, reason, and flag fields.
    input: >
      A dictionary/object containing complaint fields:
      - description (string): Text describing the issue
      - location (string, optional): Geographic location of the complaint
    output: >
      A dictionary with exactly four fields:
      - category (string): One of the 10 allowed category values
      - priority (string): Urgent, Standard, or Low
      - reason (string): One sentence citing specific words from the description
      - flag (string): "NEEDS_REVIEW" if ambiguous, empty string otherwise
    error_handling: >
      If description is empty or contains no classifiable content, set category to "Other"
      and flag to "NEEDS_REVIEW". If severity keywords are present, force priority to "Urgent"
      regardless of other factors.

  - name: batch_classify
    description: Read an input CSV file, apply classify_complaint to each row, and write the results to an output CSV file.
    input: >
      Two file paths (strings):
      - input_path: Path to input CSV with complaint data
      - output_path: Path to write classified results
    output: >
      A CSV file at output_path containing all original columns plus:
      - category, priority, reason, flag (added by classify_complaint)
    error_handling: >
      If input file cannot be read, raise a FileNotFoundError with the filename.
      If a row cannot be classified, log the row number and apply default classification
      (category: Other, priority: Low, flag: NEEDS_REVIEW) and continue processing remaining rows.
      Do not stop processing on individual row failures.
