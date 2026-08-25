skills:
  - name: classify_complaint
    description: Classify one complaint row into the approved category, priority, reason, and review flag.
    input: "A single dictionary or CSV row containing complaint_id and description along with any available civic metadata."
    output: "A dictionary with complaint_id, category, priority, reason, and flag values."
    error_handling: "If the description is empty or missing, return category Other, priority Low, a brief reason, and flag NEEDS_REVIEW instead of crashing."

  - name: batch_classify
    description: Read an input CSV, classify each complaint row, and write the results CSV with one row per complaint.
    input: "Path to an input CSV file and a target output path for the generated results CSV."
    output: "A CSV file containing the classification output for every valid row in the source file."
    error_handling: "Skip malformed rows without stopping the batch; keep valid rows, write the file, and mark insufficiently clear rows with NEEDS_REVIEW."
