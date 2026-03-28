# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint text to determine its category, priority level, justification, and review flag.
    input: A single string or dictionary representing the complaint's description text.
    output: A structured object returning four exact fields — `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If the description is ambiguous, missing, or spans multiple categories weakly, default to 'Other' category and append 'NEEDS_REVIEW' to the flag.

  - name: batch_classify
    description: Reads a CSV file of complaints, iterates over each row using the classify_complaint skill, and writes the results to a new output CSV.
    input: Filepath to the input CSV (e.g., ../data/city-test-files/test_[city].csv).
    output: A newly written CSV file at the specified output path (e.g., results_[city].csv) containing the new classification columns.
    error_handling: If the input file is missing or invalid, generate an error. If individual rows fail processing, log a warning but continue batching.
