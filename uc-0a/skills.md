# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and providing a text-based reason according to strict enforcement rules.
    input: String (complaint description).
    output: A dictionary containing 'category' (allowed taxonomy), 'priority' (Urgent/Standard/Low), 'reason' (citing description), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Sets category to 'Other' and flag to 'NEEDS_REVIEW' if categorization is ambiguous or description is insufficient.

  - name: batch_classify
    description: Reads an input CSV file containing citizen complaints, processes each row using classify_complaint, and writes the results to a specified output CSV.
    input: CSV file path (input) and CSV file path (output).
    output: A generated CSV file with classification results appended to each row.
    error_handling: Validates CSV structure and ensures all rows are processed, defaulting to 'Other'/'NEEDS_REVIEW' for unclassifiable entries.
