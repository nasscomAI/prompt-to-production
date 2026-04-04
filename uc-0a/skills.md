skills:
  - name: classify_complaint
    description: Processes a single citizen complaint row to extract and assign its category, priority, reason, and review flag.
    input: A string or parsed JSON dictionary representing a single citizen complaint description.
    output: A dictionary object containing strictly formatted 'category', 'priority', 'reason', and 'flag' string fields.
    error_handling: Return category 'Other' and set flag 'NEEDS_REVIEW' if the description is entirely unparsable, empty, or misses necessary context.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, sequentially applies the classify_complaint skill per row, and writes out the compiled structured results to an output CSV.
    input: A string filepath pointing to the input CSV file containing citizen complaints.
    output: A string filepath pointing to the generated output CSV file with appended classification columns.
    error_handling: Log file reading/writing errors; wrap row-level execution in a try-catch to apply a default 'Other'/'NEEDS_REVIEW' fallback on failure without stopping batch execution.
