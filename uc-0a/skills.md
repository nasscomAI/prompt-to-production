# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description and determines its category, priority, reason, and review flag.
    input: A single complaint description string.
    output: A dictionary containing category (string), priority (string), reason (string), and flag (string).
    error_handling: If the description is genuinely ambiguous or unrecognizable, set category to "Other" and flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and output CSV.
    output: A newly generated output CSV file containing the original data plus the classification columns.
    error_handling: If the input file is missing or unreadable, raise a FileNotFoundError or parsing exception.
