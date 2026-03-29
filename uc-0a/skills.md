skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into a strictly defined category and priority, providing a justified reason and flagging if ambiguous.
    input:
      type: string
      format: Text of the citizen complaint to be classified.
    output:
      type: dictionary
      format: Keys must include category (exact allowed string), priority (Urgent, Standard, Low), reason (one sentence), and flag (NEEDS_REVIEW or blank).
    error_handling:
      taxonomy_drift: Reject any category not in the allowed list (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other).
      severity_blindness: Force priority to Urgent if keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are detected.
      missing_justification: Output NEEDS_REVIEW flag if reason fails to cite specific words directly from the complaint description.
      false_confidence_on_ambiguity: Output NEEDS_REVIEW flag if the complaint applies to multiple categories or lacks clear details.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input:
      type: string
      format: File path to the input CSV (e.g., ../data/city-test-files/test_[your-city].csv).
    output:
      type: string
      format: File path to the output CSV (e.g., uc-0a/results_[your-city].csv).
    error_handling:
      invalid_file: Return an error message indicating the input file could not be read.
      row_processing_error: Log the error, output NEEDS_REVIEW for the flag on the failed row, and continue processing remaining rows.
