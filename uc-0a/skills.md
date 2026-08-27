# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a category and assigns priority based on severity keywords found in the description.
    input: String (the complaint description).
    output: Structured data (Category, Priority, Reason, Flag).
    error_handling: If input is empty or category is ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file containing multiple complaints, applies classify_complaint per row, and writes the results to an output CSV.
    input: CSV file path (input) and CSV file path (output).
    output: Resulting CSV file with classification columns added.
    error_handling: Logs an error if the input file is missing or contains invalid data, skipping problematic rows if necessary.
