# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint description from a citizen, classifying it into a category, assigning priority, generating a reason, and handling ambiguity with a flag.
    input: Text string containing a single citizen complaint description.
    output: A structured record containing category, priority, reason, and flag.
    error_handling: If the complaint text is genuinely ambiguous, generate the best possible fit but set the 'flag' field to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint iteratively to each row, and writes the structured classification data into an output CSV.
    input: File path to the input CSV containing stripped `category` and `priority_flag` columns (e.g. test_[your-city].csv).
    output: An output CSV containing the classification results with the newly populated structured columns (e.g. results_[your-city].csv).
    error_handling: In the event of row parse failure or unrecoverable error during row evaluation, the row's reason should note the parse problem and its flag must be set to 'NEEDS_REVIEW'. Proceed with subsequent rows.
