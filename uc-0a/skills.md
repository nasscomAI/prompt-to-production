# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A complaint description string.
    output: A dictionary object with keys: category, priority, reason, flag.
    error_handling: If input is ambiguous, returns category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, processes each row using classify_complaint, and writes results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the resulting output CSV file.
    error_handling: Handles file I/O errors and logs row-level failures while continuing processing.
