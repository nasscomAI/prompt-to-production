skills:
  - name: classify_complaint
    description: Reads one complaint record and assigns the approved category, priority level, and a justification that cites the description text.
    input: A single CSV row dictionary containing complaint_id and description plus any other fields available in the input data.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or ambiguous, return Other with NEEDS_REVIEW instead of guessing a category.

  - name: batch_classify
    description: Processes the entire complaint dataset row by row and writes the classified results as a CSV in the required output format.
    input: An input CSV path and the target output CSV path.
    output: A CSV file with complaint_id, category, priority, reason, and flag values for every row.
    error_handling: If the input file is missing or malformed, raise a clear error and stop without silently producing partial or incorrect output.
