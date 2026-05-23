skills:
  - name: classify_complaint
    description: Classifies a single unstructured citizen complaint row into predefined category, priority, justification, and ambiguity flag.
    input: A dictionary containing the keys 'complaint_id' (string) and 'description' (string).
    output: A dictionary containing the keys 'complaint_id' (string), 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: For null, empty, or missing description inputs, or for genuinely ambiguous descriptions, sets the category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV, processes each row using the classify_complaint skill, and writes results to an output CSV.
    input: Two strings representing 'input_path' (path to the input CSV file) and 'output_path' (path to save the output CSV file).
    output: Writes a CSV file with classified results, producing output and logging errors without crashing on individual row failures.
    error_handling: Handles malformed rows, null values, or individual row classification failures gracefully, logs the exceptions, and guarantees the output file is created even if some rows fail.
