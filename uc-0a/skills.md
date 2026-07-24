# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category with priority level and justification.
    input: >
      A dictionary containing complaint data with required key 'description' (string).
      Optional keys: complaint_id, date_raised, city, ward, location, reported_by, days_open.
    output: >
      A dictionary with keys:
      - complaint_id: string (passed through from input or 'UNKNOWN')
      - category: string (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
      - priority: string (one of: Urgent, Standard, Low)
      - reason: string (one sentence citing specific words from description)
      - flag: string (either 'NEEDS_REVIEW' or empty string)
    error_handling: >
      If description is missing, empty, or null: return category='Other', priority='Low', 
      reason='No description provided', flag='NEEDS_REVIEW'.
      If description is ambiguous or spans multiple categories: return the most dominant 
      category, or 'Other' if truly indeterminate, with flag='NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV file of complaints, classifies each row, and writes results to output CSV.
    input: >
      Two file paths as strings:
      - input_path: path to CSV file containing complaint data with columns including 'description'
      - output_path: path where results CSV will be written
    output: >
      Writes a CSV file to output_path with columns: complaint_id, category, priority, reason, flag.
      Returns None (side-effect function).
    error_handling: >
      If input file doesn't exist: raise FileNotFoundError with descriptive message.
      If input file is empty: write empty output CSV with headers only.
      If individual row fails classification: include row in output with category='Other', 
      priority='Low', reason='Classification failed', flag='NEEDS_REVIEW'. 
      Processing continues for remaining rows — never crash on a single bad row.
      If row has no complaint_id: generate as 'ROW_N' where N is the row number.
