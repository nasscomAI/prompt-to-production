# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint row and outputs its category, priority, reason, and flag according to strict classification schema rules.
    input: A single complaint row containing a description.
    output: Category, priority, reason, and flag (NEEDS_REVIEW or blank).
    error_handling: In cases of genuine ambiguity or unclassifiable content, set the flag to NEEDS_REVIEW. Do not hallucinate sub-categories.

  - name: batch_classify
    description: Reads an input CSV containing citizen complaints, applies classify_complaint per row, and writes an output CSV.
    input: Given input CSV file path and target output CSV file path.
    output: A written CSV file with the added classification columns.
    error_handling: Skip or output blank results for any malformed rows and gracefully continue processing the rest of the file.
