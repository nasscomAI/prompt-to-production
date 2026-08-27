# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into the required category, priority, reason, and flag fields.
    input: One complaint record as a dictionary or row object containing at least the complaint description and any available metadata from the source CSV.
    output: A normalized object with category, priority, reason, and flag using the exact allowed values from the UC-0A schema.
    error_handling: If the description is missing or too ambiguous to justify a category, return category as Other, set flag to NEEDS_REVIEW, and write a cautious reason that cites the uncertainty instead of guessing.

  - name: batch_classify
    description: Read an input CSV, apply classify_complaint to each complaint row, and write an output CSV with the required schema.
    input: An input CSV file path and an output CSV file path, where each row contains a complaint description and related fields.
    output: An output CSV file with one row per input complaint and the columns category, priority, reason, and flag.
    error_handling: Preserve row order, report or stop on missing required data, and ensure every output row follows the schema exactly even when a row is ambiguous.
