uc_id: UC-0A
title: Complaint Classifier

objective: >
  Classify citizen complaints into standardized categories and priority levels,
  ensuring strict adherence to schema, accurate severity detection, and justified outputs.

framework: RICE

reach:
  description: >
    Applies to all complaint rows in input CSV files (15 rows per city test file).
    Impacts downstream civic workflows such as escalation and response prioritization.
  scope: batch + single-row classification

impact:
  description: >
    High impact on public safety and service efficiency.
    Misclassification can delay urgent issues (e.g., injury, hazard).
  goals:
    - Enforce exact category taxonomy
    - Detect severity correctly using keywords
    - Provide transparent reasoning
    - Flag ambiguity instead of guessing

confidence:
  risks:
    - Taxonomy drift (non-standard category names)
    - Missing severity detection
    - Hallucinated sub-categories
    - Overconfident classification on unclear complaints
  mitigations:
    - Hard-coded allowed category list
    - Keyword-based urgency override
    - Mandatory reason field with evidence
    - Ambiguity flag (NEEDS_REVIEW)

effort:
  level: medium
  components:
    - Row-level classifier function
    - Batch CSV processor
    - Validation against schema
    - Keyword detection logic

classification_schema:
  category_allowed_values:
    - Pothole
    - Flooding
    - Streetlight
    - Waste
    - Noise
    - Road Damage
    - Heritage Damage
    - Heat Hazard
    - Drain Blockage
    - Other

  priority_allowed_values:
    - Urgent
    - Standard
    - Low

  severity_keywords:
    - injury
    - child
    - school
    - hospital
    - ambulance
    - fire
    - hazard
    - fell
    - collapse

  rules:
    - Use exact category strings only
    - Assign Urgent if any severity keyword is present
    - Reason must be one sentence citing words from input
    - Use NEEDS_REVIEW flag if ambiguity exists

skills:
  - name: classify_complaint
    input: single complaint row (text description)
    output:
      - category
      - priority
      - reason
      - flag
    logic:
      - Match keywords to category
      - Check severity keywords → override priority to Urgent
      - Generate one-sentence reason quoting input words
      - If unclear mapping → category=Other + flag=NEEDS_REVIEW

  - name: batch_classify
    input: CSV file (multiple complaint rows)
    output: CSV file with classifications
    steps:
      - Read input CSV
      - Apply classify_complaint per row
      - Validate outputs against schema
      - Write results to output CSV

failure_modes:
  - taxonomy_drift: non-standard category names used
  - severity_blindness: urgent keywords ignored
  - missing_reason: no justification provided
  - hallucinated_categories: categories outside allowed list
  - false_confidence: no flag on ambiguous inputs

validation_checks:
  - category must match allowed list exactly
  - priority must be one of: Urgent, Standard, Low
  - reason must exist and reference input text
  - urgency triggered if severity keywords found
  - ambiguous cases must include NEEDS_REVIEW flag

output_format:
  fields:
    - category
    - priority
    - reason
    - flag
