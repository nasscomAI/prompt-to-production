skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint based on its description into an exact category and priority level, with a justifying reason and uncertainty flag.
    input: A string containing the text description of the complaint.
    output: A structured object or dictionary containing four fields - category (string), priority (string), reason (string), and flag (string).
    error_handling: If the description is genuinely ambiguous or the category cannot be determined, returns category as "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV file, applies the classify_complaint skill to each row sequentially, and writes the results to an output CSV file.
    input: File path to the input CSV containing complaints (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Writes a new output CSV file (e.g., results_[your-city].csv) containing the original data appended with the new classification columns.
    error_handling: If the input file is not found, surface a clear file not found error. If a specific row is malformed, log a warning and skip or return empty fields for that row while continuing execution.
