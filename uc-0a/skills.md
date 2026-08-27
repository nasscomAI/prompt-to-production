# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority level, providing a specific reason and an optional review flag.
    input: A raw text string representing the citizen complaint description.
    output: A structured record or dictionary containing four fields - `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the description is genuinely ambiguous, it sets the category to 'Other' and the flag to 'NEEDS_REVIEW' instead of crashing.

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the `classify_complaint` skill to each row, and writes the results to an output CSV file.
    input: A file path to the input CSV file containing unclassified complaints (e.g., `test_[your-city].csv`).
    output: A file path to the generated output CSV file containing the classifications (e.g., `results_[your-city].csv`).
    error_handling: If the input file is missing or unreadable, throw a file not found error; if a specific row is malformed, skip or flag it and continue processing the rest of the batch.
