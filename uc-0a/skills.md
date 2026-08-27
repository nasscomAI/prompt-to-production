# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single unstructured citizen complaint description to output structured taxonomy fields mapping strictly to the operational boundaries in agents.md.
    input: Dictionary mapping containing at minimum the raw citizen text 'description'.
    output: |
      Dictionary with exactly 5 fields: complaint_id, category, priority, reason, flag
      Constraints (Per agents.md Enforcement):
      - 'category' MUST be one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
      - 'priority' MUST be one of: Urgent, Standard, Low. 
      - 'priority' MUST trigger 'Urgent' if description contains severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
      - 'reason' MUST be a single sentence strictly citing specific words found in the description.
    error_handling: |
      If the text description is missing, ambiguous, or the category cannot be confidently mathematically determined from the text alone, you MUST output category 'Other' and set the 'flag' field to 'NEEDS_REVIEW' instead of hallucinating.

  - name: batch_classify
    description: Operates the classify_complaint skill in loop over an input database to sequentially write classified outputs safely.
    input: Mapping of paths (e.g. input_path for the test CSV and output_path for the results CSV).
    output: Written results file at the output_path natively dumping all fields strictly aligned with the schema defined in agents.md.
    error_handling: Intended to swallow single row-level python crashes to ensure partially-valid results still securely output without terminating the batch loop.
