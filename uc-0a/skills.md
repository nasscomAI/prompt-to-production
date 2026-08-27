# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category, calculates priority, provides a citation-backed reason, and flags ambiguity.
    input: A single complaint text description (string).
    output: A dictionary containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: Return category "Other" and flag "NEEDS_REVIEW" if the description is entirely unintelligible, missing, or genuinely ambiguous.

  - name: batch_classify
    description: Reads a CSV of complaints, applies the classify_complaint skill to each row, and writes the results to a new output CSV.
    input: File paths for input CSV and output CSV (strings).
    output: A newly written CSV file at the output path containing original data plus classification columns.
    error_handling: Skip rows that are malformed or log an error and continue processing the rest of the batch smoothly.
