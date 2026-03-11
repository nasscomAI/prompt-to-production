skills:
  - name: classify_complaint
    description: Classifies one complaint into category and priority, with reason and flag.
    input: |
      Object with fields:
      - complaint_id: string or number
      - description: string, may be empty
      - title: optional string
    output: |
      Object with fields:
      - complaint_id
      - category: one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
      - priority: one of [Urgent, Standard, Low]
      - reason: single sentence citing specific words from description
      - flag: NEEDS_REVIEW or blank
    error_handling: |
      - Empty or missing description: category Other, priority Standard, reason notes missing/insufficient description, flag NEEDS_REVIEW.
      - Ambiguous classification: category Other, flag NEEDS_REVIEW.
      - Always return complaint_id if present; deterministic decisions.
      - Normalization: garbage/trash → Waste; lamp/light → Streetlight; drain/sewer → Drain Blockage; heat/heatwave → Heat Hazard; historic/monument → Heritage Damage; pothole → Pothole; generic road terms without 'pothole' → Road Damage.
      - Urgent triggers: if description contains any of [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse], set priority Urgent; else Standard unless clearly low severity.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes results CSV.
    input: |
      Path to CSV file containing complaint rows; expects complaint_id and description fields; extra columns are ignored.
    output: |
      CSV written to specified output path with columns: complaint_id, category, priority, reason, flag.
    error_handling: |
      - Never crash on bad rows; emit a row with category Other, priority Standard, reason noting the issue, flag NEEDS_REVIEW.
      - Flag null or empty descriptions as NEEDS_REVIEW.
      - Continue processing after errors; preserve order of input rows.
