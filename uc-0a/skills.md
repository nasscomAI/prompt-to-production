# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row to precisely categorize its domain, assess priority based on severe keywords, generate a text-justified reason, and flag review requirements for edge/ambiguous incidents.
    input: Dictionary containing complaint details (description, location, etc.).
    output: Dictionary containing keys (category, priority, reason, flag).
    error_handling: For ambiguous categories (multiple overlaps), assigns the most likely category and sets flag to NEEDS_REVIEW. Defaults missing keywords to Standard.

  - name: batch_classify
    description: Streams an entire CSV of complaints, applying `classify_complaint` line-by-line while gracefully aggregating results to a new dataset.
    input: Filepath paths for input (CSV) and output (CSV).
    output: Generates a processed CSV file enriched with category, priority, reason, and flag fields.
    error_handling: Skips completely garbled/empty rows, gracefully handling schema mutations. Ensures output proceeds.
