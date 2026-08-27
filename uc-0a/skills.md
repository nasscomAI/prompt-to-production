# skills.md

skills:
  - name: classify_complaint
    description: Evaluates a single citizen complaint description to extract category, priority, and reason.
    input: A single unstructured citizen complaint description (e.g., from a CSV row).
    output: Category, priority, reason (1 sentence citing specific words), and flag.
    error_handling: If the category is ambiguous or cannot be explicitly determined, the flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, applies the classify_complaint skill to each row, and writes an output CSV.
    input: Path to the input CSV file containing complaint descriptions.
    output: Writes a new output CSV file with identical rows plus the new category, priority, reason, and flag columns.
    error_handling: If the input file is missing or a row is malformed, skips the row or fails with an explanatory error without stalling silently.
