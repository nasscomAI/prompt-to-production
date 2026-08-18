# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag based on the description.
    input: A dictionary or row containing the complaint description (string).
    output: A dictionary with keys: category (string), priority (string), reason (string), flag (string or blank).
    error_handling: If the category cannot be determined confidently, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row using classify_complaint, and writes the results to an output CSV.
    input: Input CSV file path (string) and output CSV file path (string).
    output: Writes the classified results to the output CSV file (no return value).
    error_handling: If input file not found, raise FileNotFoundError; if output path invalid, raise appropriate error.
