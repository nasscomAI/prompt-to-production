# skills.md

skills:
  - name: classify_complaint
    description: Processes a single raw citizen complaint description and evaluates it against a predefined taxonomy to output structural classification.
    input: Raw citizen complaint description text (string).
    output: A structured object containing 'category', 'priority', 'reason' (one sentence citing input), and 'flag'.
    error_handling: If the category cannot be confidently determined or is genuinely ambiguous, it outputs 'category: Other' and 'flag: NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill row by row, and writes the results to an output CSV.
    input: File path to the input CSV file containing unclassified complaint rows.
    output: File path to the written output CSV file fully populated with classified columns.
    error_handling: Logs any file unreadability or missing columns. Skips malformed rows and safely continues processing the remainder of the valid batch.
