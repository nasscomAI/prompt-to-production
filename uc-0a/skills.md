# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and classifies it into a standardized category, priority level, reason, and review flag.
    input: A single citizen complaint text string or row data (String/Dict).
    output: A dictionary or class containing `category` (exact allowed strings), `priority` (Urgent/Standard/Low), `reason` (1 sentence citation), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the complaint description is genuinely ambiguous, cannot be determined, or is invalid, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, applies the classify_complaint skill to each row, and writes the structured results to an output CSV file.
    input: File paths for the input CSV (`--input`) and the desired output CSV (`--output`).
    output: A newly generated CSV file at the output path containing the original data merged with the new classification fields.
    error_handling: If a specific row fails classification, fallback to category "Other" with flag "NEEDS_REVIEW" and ensure the batch process continues executing without safely crashing.
