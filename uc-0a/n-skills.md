- name: classify_complaint
  description: Categorizes a single citizen complaint and assigns priority, justification, and an ambiguity flag based on the UC-0A urban maintenance schema.
  input: Object containing a 'description' string from a complaint row.
  output: Object containing 'category', 'priority', 'reason', and 'flag' fields.
  error_handling: Addresses 'False confidence on ambiguity' by setting the 'flag' to 'NEEDS_REVIEW' for non-obvious cases; prevents 'Severity blindness' by strictly enforcing 'Urgent' priority when severity keywords are detected; blocks 'Hallucinated sub-categories' by refusing to generate entries outside the approved taxonomy.
- name: batch_classify
  description: Reads an input CSV of complaints, applies individual classification logic to each row, and writes the results to a city-specific output CSV.
  input: String representing the absolute path to the stripped input CSV file.
  output: String representing the absolute path to the uc-0a/results_[city].csv output file.
  error_handling: Mitigates 'Taxonomy drift' by enforcing consistent category formatting across all rows; prevents 'Missing justification' by flagging or failing rows that lack descriptive data required for the one-sentence rule; validates input file integrity.
