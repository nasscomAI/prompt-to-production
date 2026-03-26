skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A dictionary containing complaint_id and complaint_text.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If complaint_text is missing or empty, assign category "Other", priority "Low", reason "No description provided", and flag "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes all complaints from an input CSV and writes classified results to an output CSV.
    input: Path to input CSV file.
    output: CSV file with classification results.
    error_handling: Skips malformed rows but logs them and continues processing remaining rows.