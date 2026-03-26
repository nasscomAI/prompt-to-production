# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description and returns structured classification data including category, priority, reason, and flag.
    input: A string containing the citizen's complaint description.
    output: A dictionary or JSON object containing fields: category (string), priority (string), reason (string), and flag (string or null).
    error_handling: If the description is empty or completely unintelligible, set category to 'Other', priority to 'Standard', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file containing multiple complaint records, applies the classify_complaint skill to each record, and saves the results to an output CSV.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file containing the original description along with the classification fields.
    error_handling: If the input file is missing or formatted incorrectly, log an error message and terminate the process without creating a partial output file.
