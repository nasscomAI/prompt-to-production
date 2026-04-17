# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and maps it to the city maintenance taxonomy.
    input: 
      type: string
      format: "Complaint description text (e.g., 'Huge pothole near the school entrance')"
    output: 
      type: dictionary
      schema:
        category: "One of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
        priority: "One of: Urgent, Standard, Low"
        reason: "One sentence citing specific words from description"
        flag: "NEEDS_REVIEW or blank"
    validation_rules:
      - "Set priority to 'Urgent' if keywords like 'injury', 'school', or 'hospital' are present."
      - "Set category to 'Other' and flag to 'NEEDS_REVIEW' if ambiguity is high."
    error_handling: "Return 'Other' category and 'NEEDS_REVIEW' flag for empty or unintelligible input."

  - name: batch_classify
    description: Processes a CSV file of complaints and generates a result CSV with classified fields.
    input: 
      type: string
      format: "Path to input CSV (e.g., ../data/city-test-files/test_pune.csv)"
    output: 
      type: string
      format: "Path to output CSV (e.g., results_pune.csv)"
    constraints:
      - "Must not crash on null actual_spend rows or missing notes."
      - "Must produce a result for every row in the input file."
    error_handling: "Log missing file errors and terminate; for row-level errors, skip and flag the row."
