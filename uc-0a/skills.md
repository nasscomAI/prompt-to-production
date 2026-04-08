# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag fields based on the description text and severity keywords.
    input: A dictionary/object containing complaint description text (string)
    output: A dictionary with keys: category (string), priority (string), reason (string), flag (string or null)
    error_handling: If description is empty or category cannot be determined, return category='Other' and flag='NEEDS_REVIEW'

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file with classified columns.
    input: Two file paths — input CSV path and output CSV path
    output: CSV file with same rows as input plus columns: category, priority, reason, flag
    error_handling: If input file is missing or malformed, raise an error with specific message; log warning for any individual row that requires NEEDS_REVIEW flag
