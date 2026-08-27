skills:
  - name: complaint_text_analysis
    description: Analyze the complaint description text and identify keywords related to service issues.
    input: Complaint description text (string) from the input CSV row.
    output: Identified issue keywords and suggested complaint category.
    error_handling: If the description is empty or unclear, return category "Other" and flag "NEEDS_REVIEW".

  - name: priority_detection
    description: Determine the priority level of the complaint based on risk-related keywords.
    input: Complaint description text (string).
    output: Priority level as "Urgent" or "Normal".
    error_handling: If no priority keywords are detected, return priority "Normal".

  - name: complaint_classification
    description: Classify the complaint into predefined categories such as Pothole, Flooding, Garbage, Streetlight, Water Supply, or Other.
    input: Complaint description text (string).
    output: Category label (string) and short reason explaining the classification.
    error_handling: If category cannot be determined, return category "Other" and add flag "NEEDS_REVIEW".

  - name: csv_batch_processing
    description: Process multiple complaints from an input CSV file and generate classified results.
    input: CSV file containing complaint_id and description fields.
    output: Output CSV file with complaint_id, category, priority, reason, and flag.
    error_handling: If a row contains missing or invalid data, skip the row or flag it as "FAILED_ROW" without stopping the program.