# skills.md

skills:
  - name: classify_complaint
    description: Evaluates a single stripped citizen complaint description and maps it to a rigid output structure consisting of exactly 4 fields (category, priority, reason, flag) complying with the City schema.
    input: A single raw string from a CSV representing the complaint description.
    output: A precise structured dictionary containing `category` (1 of 10 fixed strings), `priority` ('Urgent', 'Standard', or 'Low'), `reason` (one-sentence string quoting text), and `flag` ('NEEDS_REVIEW' or blank).
    error_handling: If the input description is completely unreadable, missing, or fundamentally ambiguous making single-category isolation impossible, the skill MUST return `category` as 'Other' and `flag` as 'NEEDS_REVIEW'. Do not throw a hard error; gracefully handle ambiguous text.

  - name: batch_classify
    description: Consumes the input test CSV file (15 rows), executes 'classify_complaint' per row, validates the strict structural schema, and writes the required output CSV file.
    input: A valid filepath string pointing to the source CSV (e.g., '../data/city-test-files/test_[your-city].csv').
    output: A valid filepath string pointing to the destination output CSV (e.g., 'uc-0a/results_[your-city].csv').
    error_handling: If the source CSV is missing, halt execution and raise a filepath validation error. If the 'classify_complaint' skill fails critically on any specific row during batch processing, handle the exception by falling back to `category`: 'Other' and `flag`: 'NEEDS_REVIEW' for that row, ensuring the output file is still generated with exactly 15 valid rows.
