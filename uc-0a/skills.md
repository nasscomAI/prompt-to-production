# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into predefined categories and priorities based on specific rules.
    input: A single dictionary representing a complaint row, containing the complaint description and metadata.
    output: A dictionary containing the original complaint_id, along with exactly four assigned fields: category (string), priority (string), reason (string), and flag (string).
    error_handling: If the input is invalid or cannot be parsed, return the row with category "Other", flag "ERROR", and reason noting the parsing failure.

  - name: batch_classify
    description: Processes a batch of complaints from an input CSV file and writes the classified results to an output CSV file.
    input: An input file path (string) pointing to a CSV of complaints, and an output file path (string) for the results.
    output: None (writes a CSV file to the output path).
    error_handling: Must flag nulls or bad rows, gracefully continue processing without crashing on errors, and ensure an output file is produced even if some rows fail.
