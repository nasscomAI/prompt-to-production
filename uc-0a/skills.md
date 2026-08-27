# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to map it to a specific category and priority with a cited reason.
    input: A string or JSON object containing the citizen's complaint description.
    output: >
      A structured JSON object with fields: 
      - category (string: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other)
      - priority (string: Urgent, Standard, or Low)
      - reason (string: One sentence citing specific words from description)
      - flag (string: "NEEDS_REVIEW" or blank)
    error_handling: If the description is too sparse to classify, set category to "Other" and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Processes multiple complaints from a source file and generates a formatted results file.
    input: A CSV file located at ../data/city-test-files/test_[city].csv.
    output: A CSV file named uc-0a/results_[city].csv containing columns for category, priority, reason, and flag.
    error_handling: Logs rows that fail validation against the taxonomy and ensures the output file matches the input row count exactly.
