skills:
  - name: classify_complaint
    description: Classifies a single complaint into a valid category, assigns priority based on severity keywords, provides a justification, and flags ambiguity.
    input: complaint description (string)
    output:
      - category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
      - priority (Urgent / Standard / Low)
      - reason (one sentence citing exact words from the input)
      - flag (NEEDS_REVIEW or blank)
    error_handling: 
      - If category cannot be confidently determined → set category = Other and flag = NEEDS_REVIEW
      - If severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present → priority MUST be Urgent
      - Never invent categories outside the allowed list
      - Never skip the reason field
      - Never ignore severity keywords

  - name: batch_classify
    description: Reads a CSV of complaint descriptions, applies classify_complaint to each row, and writes structured results to an output CSV.
    input: input CSV file path (string)
    output: output CSV file with columns: category, priority, reason, flag
    error_handling:
      - If input file is missing or invalid → raise clear error
      - If a row is ambiguous → apply fallback (category = Other, flag = NEEDS_REVIEW)
      - Never stop processing entire file due to a single bad row