skills:
  - name: classify_complaint
    description: "Classify one citizen complaint row into the fixed category and priority schema, with evidence and ambiguity handling."
    input: "One complaint row containing a description string."
    output: "One result containing category, priority, reason, and flag. category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. priority must be exactly one of: Urgent, Standard, Low. reason must be one sentence citing specific words from the description. flag must be NEEDS_REVIEW or blank."
    error_handling: "If the category is genuinely ambiguous or cannot be determined from the description alone, use category Other and flag NEEDS_REVIEW. Do not invent sub-categories or unsupported facts."

  - name: batch_classify
    description: "Read a city complaint CSV, classify every row with classify_complaint, and write the resulting CSV."
    input: "CSV path matching ../data/city-test-files/test_[your-city].csv; category and priority_flag columns are stripped and each city file contains 15 rows."
    output: "CSV at the requested output path, with one result row per input row and classification fields category, priority, reason, and flag."
    error_handling: "Apply classify_complaint independently to each row, preserving row count. For ambiguous descriptions, use category Other and flag NEEDS_REVIEW. Reject or report malformed input rather than fabricating missing complaint text."
