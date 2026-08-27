skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to extract category, priority, justification, and review flags.
    input: A string representing a single unclassified citizen complaint.
    output: A structured mapping of exactly four fields (category, priority, reason, flag).
    error_handling: If the complaint description is completely unreadable or lacks critical context, output category as 'Other' and flag as 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, processes each using classify_complaint, and writes the compiled results to an output CSV.
    input: Filepath to an input CSV containing complaints (e.g., ../data/city-test-files/test_pune.csv).
    output: Filepath to a completed output CSV (e.g., results_pune.csv).
    error_handling: If an individual row cannot be parsed, assign it 'NEEDS_REVIEW' and continue. If the input file is missing, fail immediately indicating the missing resource.
