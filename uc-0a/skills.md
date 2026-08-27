# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to extract its category, priority, a justification, and an ambiguity flag.
    input: A single complaint description string from a CSV row.
    output: A dictionary with keys: category, priority, reason, and flag.
    error_handling: Output category as "Other" and flag as "NEEDS_REVIEW" if the text is missing or meaningless, and default to a standard priority level. 

  - name: batch_classify
    description: Processes a list of complaints from an input CSV by applying the `classify_complaint` skill to each row and appending the classification results to an output CSV.
    input: A CSV file containing citizen complaints data (found in ../data/city-test-files/).
    output: An output CSV file with results_[city].csv format containing the added classification columns.
    error_handling: Log errors for malformed rows and continue processing; safely handle absent or null fields in the input data.
