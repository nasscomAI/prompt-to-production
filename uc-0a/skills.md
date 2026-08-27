# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint to determine its category, priority, reason, and flag based on predefined taxonomy.
    input: A single row or text description of a citizen complaint.
    output: A structured classification containing exactly four fields (category, priority, reason, flag).
    error_handling: If the description is genuinely ambiguous, unclear, or lacks sufficient detail, classification continues but the flag MUST be set to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: A file path to an input CSV (e.g., test_[city].csv with raw complaint rows).
    output: A file path to a generated output CSV (e.g., results_[city].csv) populated with the corresponding classification fields.
    error_handling: If the input file is missing or malformed, raise an appropriate file error. If an individual row fails parsing or classification, log the failure and continue processing subsequent rows.
