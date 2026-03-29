# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint to exactly one category from the schema, assign priority, and provide reasoning citing specific terms.
    input: A single citizen complaint text description (string).
    output: A JSON record containing exactly four fields (category (string), priority (string), reason (string), flag (string or blank)).
    error_handling: If the category is ambiguous or cannot be confidently classified, output category as 'Other' and flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Process a CSV file of multiple citizen complaints, iteratively applying `classify_complaint` to each row and appending the generated fields.
    input: An input CSV file path containing raw citizen complaint records.
    output: Writes a new CSV file to disk enriched with the classification results (category, priority, reason, flag).
    error_handling: If an individual complaint throws an error or cannot be parsed, log the error, skip to the next row, and ensure the pipeline continues processing.
