skills:
  - name: classify_complaint
    description: Classifies a complaint into category, priority, and generates a reason.
    input: A dictionary containing complaint_id and complaint text.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If complaint text is missing or unclear, assigns category "Other" and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes multiple complaints from a CSV file and writes classified results to another CSV.
    input: Input CSV file path with complaint data.
    output: Output CSV file with classified complaint results.
    error_handling: Skips invalid rows, writes default error output with flag "NEEDS_REVIEW" without stopping execution.
