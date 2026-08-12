# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint description into category, priority, reason, and flag.
    input: A string containing the citizen complaint description.
    output: A dict with keys {category, priority, reason, flag}.
    error_handling: If description is empty or null, return category=Other, priority=Low, reason="No description provided", flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to every row, and write results CSV.
    input: File path to input CSV (containing a description column), and file path for output CSV.
    output: A CSV file with all original columns plus category, priority, reason, flag.
    error_handling: Skip rows with missing description but continue processing; never crash mid-batch.
