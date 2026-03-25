skills:
  - name: classify_complaint
    description: Takes one row of a citizen complaint and returns it with category, priority, reason, and flag.
    input: String - the complaint description.
    output: JSON structured object containing category (string), priority (string), reason (string), and flag (string).
    error_handling: Return category "Other" and flag "NEEDS_REVIEW" if classification is ambiguous or fails.

  - name: batch_classify
    description: Reads the input CSV row by row, applies classify_complaint to each complaint, and writes the results to an output CSV.
    input: String - filepath to the input CSV representing citizen complaints.
    output: String - filepath to the output CSV containing classification results.
    error_handling: Skip the invalid row and continue processing, logging the error.
