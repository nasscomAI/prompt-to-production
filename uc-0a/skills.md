# skills.md — UC-0A Complaint Classifier Skills
# Aligned with agents.md RICE enforcement

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag fields following agents.md enforcement rules.
    
    input: |
      Dict with keys: complaint_id, description, date_raised, city, ward, location, reported_by, days_open.
      Critical field: description (string, required; acts as sole source of classification truth).
      Other fields: passed through for context only; do NOT trigger external knowledge or cross-complaint reasoning.
    
    output: |
      Dict with keys:
      - complaint_id: exact copy from input (or 'UNKNOWN' if missing)
      - category: exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Drain Blockage, Other]
      - priority: one of [Urgent, Standard, Low]; Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse (case-insensitive)
      - reason: one sentence max, must cite 2+ specific words/phrases directly from the input description (never generic, never fabricated)
      - flag: "NEEDS_REVIEW" if multiple categories plausible (>2 keyword matches); otherwise empty string
    
    enforcement:
      - "E1_category: Category must match schema exactly (agents.md). No variations, no compound categories (e.g., 'Pothole/Road Damage' is invalid)."
      - "E2_priority: Set Urgent immediately if ANY severity keyword detected (case-insensitive: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse). Otherwise Standard or Low (agents.md)."
      - "E3_reason: One sentence max. Must cite 2+ specific words/phrases from this row's description only. Reject generic ('complaint received') or fabricated reasons (agents.md)."
      - "E4_flag: Set 'NEEDS_REVIEW' if multiple categories are genuinely plausible (>2 keyword matches). Otherwise blank (agents.md)."
      - "E5_validation: complaint_id must be non-empty AND category from allowed list. If either fails, output: category=Other, priority=Standard, flag=NEEDS_REVIEW (agents.md)."
    
    error_handling: |
      If complaint_id is missing or empty: output complaint_id='UNKNOWN', category=Other, priority=Standard, flag=NEEDS_REVIEW.
      If description is empty/null: category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW.
      If description matches no category keywords: category=Other, priority=Standard (unless severity words preset→Urgent), flag blank unless ambiguous.

  - name: batch_classify
    description: Read input CSV, apply classify_complaint independently to each row, write results CSV with all rows processed (no failures silently dropped).
    
    input: |
      - input_path (str): CSV file with columns: complaint_id, description, date_raised, city, ward, location, reported_by, days_open.
      - output_path (str): Path where results CSV will be written.
    
    output: |
      CSV file (UTF-8) with columns: complaint_id, category, priority, reason, flag.
      Row count: one row per input complaint (skipped_blanks excluded from count if complaint_id filtering applied).
      All rows produced even if some rows fail individual classification (E5_validation fallback applied).
      Final print: "Done. Results written to {output_path}"
    
    enforcement:
      - "E1_read: Read all rows from input_path; skip only rows where complaint_id is empty or completely missing."
      - "E2_independent: Apply classify_complaint to each row independently. No cross-row state, no pattern learning across complaints (agents.md)."
      - "E3_output: Write header row: complaint_id,category,priority,reason,flag. All required fields present for every output row."
      - "E4_preservation: Each row: preserve input complaint_id and include all output fields. Do not truncate or omit."
      - "E5_completeness: Produce output CSV even if some rows fail. Fallback: output rows with category=Other, priority=Standard, flag=NEEDS_REVIEW per E5_validation."
    
    error_handling: |
      If input_path does not exist or is unreadable: print error message and return gracefully (do not crash).
      If a single row fails classification (encoding error, etc.): log warning, output fallback record (category=Other, priority=Standard, flag=NEEDS_REVIEW), continue processing.
      If output_path is unwritable: print error message and return gracefully.
      If input_path is empty (0 rows): print warning and create empty output CSV with headers only.
