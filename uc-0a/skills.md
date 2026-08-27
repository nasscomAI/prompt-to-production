# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row by parsing its description into a structured classification.
    input: A single complaint row (string description or JSON/dictionary of row data).
    output: A structured object/dictionary with exactly four fields - category (string), priority (string), reason (string), and flag (string).
    error_handling: If the complaint description is ambiguous or unclear, the category can be a best guess or 'Other', but the `flag` field must be explicitly set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of multiple complaints, applies classify_complaint to each row, and writes the classifications to an output CSV.
    input: File path containing the input CSV data (e.g., ../data/city-test-files/test_[your-city].csv).
    output: A generated CSV file saved to the specified output path (e.g., uc-0a/results_[your-city].csv).
    error_handling: Skip or log empty rows. If writing fails, throw an IO error. If an individual row classification errors out completely, leave fields blank and add 'ERROR' to the flag column.
