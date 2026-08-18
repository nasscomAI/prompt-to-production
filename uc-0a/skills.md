# skills.md

skills:
  - name: classify_complaint
    description: Expert prompt skill to classify a single municipal complaint text into category, priority, reason, and flag using UC-0A taxonomy and urgency rules.
    input: A single string containing the complaint text (`complaint_text`).
    output: A raw JSON object string with keys `category`, `priority`, `reason`, `flag`.
    error_handling: If input is empty or not clearly mappable, return `category: Other`, `priority: Standard`, a reason that cites the input text when possible, and `flag: NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads CSV rows of complaints and applies `classify_complaint` to each row.
    input: CSV input path or in-memory list of complaint text rows.
    output: CSV output path or data with columns `category`, `priority`, `reason`, `flag`.
    error_handling: Logs row-level failures, uses `NEEDS_REVIEW` for ambiguous rows, continues processing remaining rows.

craft_prompt_template: |
  Context: You are a UC-0A Complaint Classifier. Use README rules as the supreme source: categories exactly Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Priorities are exactly Urgent, Standard, Low. Severity keywords force Urgent.
  Role: Expert Civic Data Classifier.
  Action: Analyze {complaint_text} and return structured classification.
  Format: Produce only raw JSON text with keys category, priority, reason, flag. Do not use markdown code fences or any extra prose.
  Target: {complaint_text}

  Output Example:
  {"category":"Pothole","priority":"Urgent","reason":"Report says pothole on Main St near school, injury hazard","flag":""}

