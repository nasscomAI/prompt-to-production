# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row by assigning category, priority, and justification based on description text.
    
    input: >
      dict with keys: complaint_id (str), description (str)
    
    output: >
      dict with keys: complaint_id (str), category (str), priority (str), reason (str), flag (str)
      where category is one of 10 allowed values, priority is Urgent/Standard/Low,
      reason cites specific words from description, and flag is NEEDS_REVIEW or blank.
    
    error_handling: >
      If description is null/empty: return category=Other, priority=Low, flag=NEEDS_REVIEW, reason="Empty description".
      If complaint_id is missing: raise ValueError.
      If category cannot be confidently determined: return category=Other, flag=NEEDS_REVIEW, reason explaining ambiguity.
    
    enforcement:
      - "Category must match exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
      - "Priority is Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
      - "Reason must be one sentence citing specific words from the description"
      - "Set flag=NEEDS_REVIEW when category is ambiguous, otherwise leave blank"

  - name: batch_classify
    description: Reads input CSV of complaints, applies classify_complaint to each row, and writes results CSV with graceful error handling.
    
    input: >
      input_path (str): path to CSV file with columns complaint_id and description.
      output_path (str): path where results CSV should be written.
    
    output: >
      No return value (side effect: writes CSV file to output_path).
      Output CSV has columns: complaint_id, category, priority, reason, flag.
      Prints summary: "Processed X rows, Y flagged for review".
    
    error_handling: >
      If input file missing/unreadable: raise FileNotFoundError with clear message.
      If row is malformed: write to output with flag=NEEDS_REVIEW and reason="Malformed row".
      If output path is unwritable: raise IOError.
      Must process all rows even if some fail — never halt processing mid-file.
    
    enforcement:
      - "Read CSV with utf-8 encoding and handle BOM if present"
      - "Write output CSV with header: complaint_id,category,priority,reason,flag"
      - "Failed rows must appear in output with flag=NEEDS_REVIEW explaining the error"
      - "Never skip rows — all input rows must appear in output"
