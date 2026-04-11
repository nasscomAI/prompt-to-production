# skills.md

skills:
  - name: classify_complaint
    description: Transforms a single raw complaint description into a structured classification (category, priority, reason, flag).
    input: A string containing the citizen's complaint report.
    output: A structured object with fields: category (string), priority (string), reason (string), flag (string).
    error_handling: For ambiguous text, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a city's complaint dataset from a CSV source to a classified CSV output.
    input: Path to a CSV file containing a column of complaint descriptions.
    output: Path to a result CSV file containing the classifications for all rows.
    error_handling: Identifies rows with missing descriptions and marks them for manual review via the flag field.
