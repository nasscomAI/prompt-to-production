skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag fields according to the fixed taxonomy and severity rules.
    input:
      type: object
      format: "{description: string}"
    output:
      type: object
      format: "{category: 'Pothole'|'Flooding'|'Streetlight'|'Waste'|'Noise'|'Road Damage'|'Heritage Damage'|'Heat Hazard'|'Drain Blockage'|'Other', priority: 'Urgent'|'Standard'|'Low', reason: string, flag: 'NEEDS_REVIEW'|''}"
    error_handling: Returns category='Other', priority='Low', reason='Unable to classify: invalid or empty description', flag='NEEDS_REVIEW' when input description is missing, empty, or unparseable; sets flag='NEEDS_REVIEW' when category is genuinely ambiguous per taxonomy rules.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each row, and writes results to an output CSV with the required schema.
    input:
      type: file
      format: CSV with columns including 'description' (path provided via --input flag)
    output:
      type: file
      format: CSV with columns 'category', 'priority', 'reason', 'flag' (path provided via --output flag)
    error_handling: Skips rows with missing/invalid descriptions and logs error with row index; continues processing remaining rows; writes partial results to output; exits with non-zero code if input file not found or unreadable.    
