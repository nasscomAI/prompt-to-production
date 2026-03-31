skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint description into an exact predefined category, priority level, justification reason, and review flag, strictly enforcing the rules established in agents.md. 
      It actively avoids taxonomy drift, severity blindness, missing justifications, hallucinated sub-categories, and false confidence on ambiguity.
    input: >
      A single raw complaint text description (String).
    output: >
      A structured object containing exactly:
      - 'category': Exact string match from [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other].
      - 'priority': 'Urgent' if severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present. Otherwise, 'Standard' or 'Low'.
      - 'reason': Exactly one sentence explicitly citing specific words from the description.
      - 'flag': 'NEEDS_REVIEW' if ambiguous, otherwise blank.
    error_handling: >
      If the complaint category is genuinely ambiguous or cannot be determined solely from the description, it must prevent false confidence by outputting category as 'Other' and strictly setting the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: >
      Reads an input CSV file of citizen complaints, iteratively applies classify_complaint to each row's description, and writes the results back to an output CSV file, adhering to the schemas outlined in agents.md.
    input: >
      File path to an input CSV containing multiple complaint rows (e.g., ../data/city-test-files/test_[your-city].csv).
    output: >
      File path to a resulting output CSV containing the successfully classified rows, appending the required 'category', 'priority', 'reason', and 'flag' fields (e.g., results_[your-city].csv).
    error_handling: >
      If a row is completely empty or cannot be parsed from the CSV, it gracefully skips or logs the problematic row without halting the processing of subsequent rows. Ensures all rows process robustly.
