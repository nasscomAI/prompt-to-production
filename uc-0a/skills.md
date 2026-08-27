skills:
  - name: classify_complaint
    description: |
      Classify a single complaint row by analyzing description text against the 
      fixed taxonomy. Output category, priority, justification, and ambiguity flag.
    
    input:
      type: dict
      schema:
        id: string (complaint identifier)
        description: string (raw complaint text)
    
    output:
      type: dict
      schema:
        category: string (Pothole|Flooding|Streetlight|Waste|Noise|Road Damage|Heritage Damage|Heat Hazard|Drain Blockage|Other)
        priority: string (Urgent|Standard|Low)
        reason: string (single sentence citing description)
        flag: string (NEEDS_REVIEW if ambiguous, else empty)
    
    error_handling:
      - Empty description: category=Other, priority=Low, flag=NEEDS_REVIEW
      - Multiple category matches: flag=NEEDS_REVIEW, use first match
      - Severity keywords present: priority=Urgent (override)
      - Cannot extract reason: use generic fallback
  
  - name: batch_classify
    description: |
      Read input CSV with complaint descriptions, apply classify_complaint to each row, 
      validate output, write results to output CSV with all columns preserved.
    
    input:
      type: file (CSV)
      required_columns: [description]
      processing: strip whitespace, skip empty rows, halt on unrecoverable format error
    
    output:
      type: file (CSV)
      columns: [id, description, category, priority, reason, flag] + preserved columns
      format: UTF-8, standard CSV
    
    error_handling:
      - Missing description column: halt with error
      - Empty row: skip silently
      - Invalid CSV format: halt with line number
      - Row classification error: set flag=NEEDS_REVIEW