skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and classifies it.
    input: A single string containing the text of the citizen complaint.
    output: A structured mapping/object containing exactly four fields - category (exact string), priority (Urgent/Standard/Low), reason (single sentence with citations), and flag (NEEDS_REVIEW or blank).
    error_handling: If the input is fundamentally ambiguous or incomprehensible, sets category to 'Other', priority based on any available keywords, flag to 'NEEDS_REVIEW', and notes the ambiguity in the reason field.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, processes each using classify_complaint, and writes the results to an output CSV.
    input: File paths defining the input CSV (e.g., test_[city].csv) and the desired output CSV (e.g., results_[city].csv).
    output: Processing confirmation and generation of the output CSV file containing the classifications appended to the original dataset.
    error_handling: Skips rows that cannot be processed due to critical missing input columns, logging an error, but continues to process the remainder of the CSV file.
