# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag based on description text alone.
    input: Dictionary with keys complaint_id and description; description is complaint text string.
    output: Dictionary with keys category (from allowed list), priority (Urgent/Standard/Low), reason (one sentence citing 2+ specific words from description), flag (NEEDS_REVIEW or blank).
    
    constraints:
      allowed_categories: [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
      severity_keywords: [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse]
      taxonomy_rule: "Category names must be exact matches from allowed list — no variations, abbreviations, or synonyms."
      priority_rule: "Priority=Urgent if ANY severity keyword present in description. Otherwise determine Standard vs Low from complaint scope."
      reason_rule: "Reason must cite 2+ specific words directly from description text; must be exactly one sentence."
      ambiguity_rule: "If category cannot be determined from description alone OR description contradicts taxonomy, output category=Other and flag=NEEDS_REVIEW; never guess with low confidence."
    
    error_handling: 
      - "Empty/null description: category=Other, priority=Standard, flag=NEEDS_REVIEW"
      - "No matching category: category=Other, flag=NEEDS_REVIEW"
      - "Cannot form reason sentence: flag=NEEDS_REVIEW"
      - "Ambiguous/contradictory description: category=Other, flag=NEEDS_REVIEW"
      - "Never output category not in allowed_categories list"

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to each row, write results CSV with classification outputs.
    input: Path to input CSV file with columns complaint_id and description; output path string.
    output: CSV file written to output path with columns complaint_id, category, priority, reason, flag. Rows written in input order; all rows included.
    
    constraints:
      consistency_rule: "Same complaint type must receive same category across rows — enforce via complaint_id and description matching."
      no_hallucination: "Do not invent categories or sub-categories not in allowed_categories."
      severity_detection: "Never classify injury/child/school complaints as Standard or Low; detect severity keywords consistently across rows."
    
    error_handling: 
      - "Per-row errors: log but continue processing; write output row with category=Other, flag=NEEDS_REVIEW"
      - "Missing complaint_id: generate placeholder id_missing_N or use row index"
      - "Malformed CSV or null values: skip field validation, use empty string as default, write row"
      - "File I/O error: raise exception with row context"
      - "Ensure partial results are written even if some rows fail"
