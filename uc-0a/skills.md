# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into the fixed taxonomy and return priority, one-sentence evidence-based reason, and ambiguity flag.
    input: |
      Type: dict (one CSV row).
      Expected keys: complaint_id plus a complaint text field (e.g., description/details/text).
      The function must tolerate missing or malformed text fields.
    output: |
      Type: dict with exact keys:
      - complaint_id
      - category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other)
      - priority (one of: Urgent, Standard, Low)
      - reason (exactly one sentence citing words/phrases from the complaint text)
      - flag (NEEDS_REVIEW or blank)
    error_handling: |
      - If complaint text is empty/malformed/insufficient, return category=Other, priority=Standard (or Urgent only when a severity keyword is explicitly present), a one-sentence missing-info reason, and flag=NEEDS_REVIEW.
      - If category is ambiguous or conflicting, prefer conservative output with category=Other and flag=NEEDS_REVIEW.
      - Enforce mandatory escalation to priority=Urgent when text contains any severity keyword (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.

  - name: batch_classify
    description: Read an input CSV, classify each row independently using classify_complaint, and always write an output CSV.
    input: |
      Type: (input_path: str, output_path: str).
      input_path points to test_[city].csv where category/priority labels are absent.
    output: |
      Type: CSV file written to output_path.
      Output columns per row (exact): complaint_id, category, priority, reason, flag.
    error_handling: |
      - Process rows independently and never crash the whole run due to one bad row.
      - For per-row failures, emit a safe fallback row with complaint_id if available, category=Other, priority=Standard (or Urgent if severity keyword explicitly present), one-sentence failure reason, and flag=NEEDS_REVIEW.
      - Ensure output CSV is always produced, even if some rows fail.
