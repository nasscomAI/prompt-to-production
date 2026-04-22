# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a complaint description to determine its category, priority, and justification according to the municipal schema.
    input: 
      type: object
      fields:
        description: string (e.g., "Deep pothole near bus stop. School children at risk.")
    output: 
      type: object
      fields:
        category: string (Must be Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other)
        priority: string (Urgent if description involves injury, children, hospitals, etc.; otherwise Standard or Low)
        reason: string (One sentence citing specific words from description)
        flag: string ('NEEDS_REVIEW' if category is ambiguous; otherwise blank)
    error_handling: Refuses to classify if description is missing; defaults to 'Other' with NEEDS_REVIEW if description is unintelligible.

  - name: batch_classify
    description: Executes a bulk classification task on a city-specific CSV file.
    input:
      type: file_path
      format: CSV (Columns: complaint_id, date_raised, city, ward, location, description, reported_by, days_open)
    output:
      type: file_path
      format: CSV (Original columns + category, priority, reason, flag)
    error_handling: Validates that input CSV contains a 'description' column; logs skipping of rows with empty descriptions.
