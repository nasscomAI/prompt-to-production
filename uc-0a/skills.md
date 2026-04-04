# skills.md

skills:
  - name: classify_complaint
    description: Processes a single complaint row and outputs its assigned category, priority, reason, and flag.
    input: A single citizen complaint row data (containing complaint description).
    output: A structured record or dictionary with EXACTLY four fields - category, priority, reason, and flag.
    error_handling: If the text is ambiguous, outputs the closest matching category or 'Other' and sets the flag to 'NEEDS_REVIEW' instead of failing or hallucinating a category.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File path to the input CSV (e.g., test_[your-city].csv).
    output: Written output CSV file (e.g., results_[your-city].csv) containing classified rows.
    error_handling: If a row cannot be processed, it skips the row or writes fallback empty/failed values to ensure the output CSV generation completes successfully.
