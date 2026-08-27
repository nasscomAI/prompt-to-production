# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description.
    input: A dictionary representing a complaint row with a 'description' field (string).
    output: A dictionary with keys 'category' (string), 'priority' (string), 'reason' (string), 'flag' (string or empty).
    error_handling: If the description is ambiguous or category cannot be determined, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Input CSV file path (string), output CSV file path (string).
    output: Writes a CSV file with columns category, priority, reason, flag for each input row.
    error_handling: Validates that input file exists and is readable; handles CSV parsing errors by logging and skipping invalid rows.
