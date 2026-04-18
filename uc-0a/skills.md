# skills.md
skills:
  - name: classify_complaint
    description: Classifies a single raw citizen complaint description by assigning a category, determining priority based on severity keywords, and generating a text-cited reason.
    input: A single raw complaint text description (string).
    output: A structured object containing category, priority, reason (one sentence), and flag.
    error_handling: If the complaint is genuinely ambiguous, set the flag to "NEEDS_REVIEW" and avoid confidently guessing.

  - name: batch_classify
    description: Reads complaints from an input CSV, evaluates each row using classify_complaint, and writes all results to an output CSV.
    input: Filepath to the input CSV file containing complaint rows.
    output: Filepath to the generated output CSV file containing the classified rows.
    error_handling: If the file is missing or malformed, raise an IO error. If an individual row fails processing, log the error and continue to the next row.
