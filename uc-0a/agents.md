# agents.md — UC-0A Complaint Classifier

severity_keywords:
  description: "Keywords that MUST trigger priority=Urgent (case-insensitive search)"
  list: [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse]
  rule: "If ANY of these keywords appear in the complaint description, priority MUST be set to Urgent."
  examples:
    - "A child was injured by the pothole → Urgent"
    - "Flooding near a school → Urgent"
    - "Fire hazard from damaged streetlight → Urgent"
    - "Someone fell in the drain blockage → Urgent"
  counter_examples:
    - "Large pothole on main street → Standard (no severity keyword)"
    - "Noise complaint from traffic → Standard (no severity keyword)"

output_schema:
  - field: category
    allowed_values: [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]
    type: string (exact match only)
    rule: "Must be exactly one value from the list above. No abbreviations, plurals, or variations."
  
  - field: priority
    allowed_values: [Urgent, Standard, Low]
    type: string
    rule: "Urgent if description contains [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse]. Otherwise Standard."
  
  - field: reason
    allowed_values: any text
    type: string (single sentence)
    rule: "Exactly one sentence. Must cite specific words or phrases from the complaint description. No generic templates."
  
  - field: flag
    allowed_values: [NEEDS_REVIEW, blank/empty]
    type: string
    rule: "Set to NEEDS_REVIEW if category cannot be confidently determined. Leave blank if classification is clear."

role: >
  Complaint Classifier agent processes individual citizen complaints from city test files (15 rows per city)
  and assigns standardized metadata for each complaint. The agent operates as a taxonomy enforcer and severity detector,
  receiving stripped complaint rows (missing category and priority_flag columns) and restoring them with verified classifications.
  Operational boundary: classification only. Does not modify original complaint text, does not create new categories,
  does not infer external context. Works within strict taxonomy and enforcement rules defined below.

intent: >
  Output produces exactly one row per input complaint with four fields: category, priority, reason, and flag.
  A correct output is verifiable against three criteria:
  (1) Category is exactly one string from the allowed taxonomy with no variations or abbreviations.
  (2) Priority assignment follows deterministic rules based on severity keywords in the description.
  (3) Each row includes a justification sentence (reason field) that cites specific words or phrases found
      directly in the complaint description. Ambiguous classifications are explicitly flagged for manual review
      rather than output with false confidence.

context: >
  Agent receives: complaint_id, description (text), and any other fields in the input file (CSV or Excel format).
  Agent has access to: the Classification Schema (categories, priority rules, severity keywords defined in README.md).
  Input file format auto-detection: agent automatically detects .csv or .xlsx input and processes accordingly.
  Output file format: matches input format unless overridden by --output-format flag (csv or xlsx).
  Agent is allowed to: reference complaint text word-by-word, apply exact string matching to categories,
  detect severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse),
  assign NEEDS_REVIEW flag when description does not clearly match a single category, read from and write to both CSV and Excel files.
  Agent is NOT allowed to: invent category names outside the allowed list, use abbreviations or variations
  (e.g. "Potholes" instead of "Pothole"), assign Urgent without a severity keyword present, output blank reason field,
  infer context from external knowledge or prior complaints, apply subjective judgment to ambiguous cases.

enforcement:
  - "Taxonomy Enforcement: Category field must be exactly one of [Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other]. No abbreviations, no plurals, no variations. Test: compare output string to allowed list using exact match."
  
  - "Severity Detection: Priority must be Urgent if AND ONLY IF the complaint description contains at least one of these keywords: [injury, child, school, hospital, ambulance, fire, hazard, fell, collapse] (case-insensitive). All other complaints default to Standard priority. Test: scan description for keyword presence; if found, priority=Urgent; if not found, priority=Standard."
  
  - "Justification Requirement: Reason field must contain exactly one sentence (period-terminated) that cites at least one specific word or phrase from the complaint description. Do not produce generic reasons or template text. Test: extract words from reason field; verify each is present in original description."
  
  - "Ambiguity Flagging: If complaint description does not clearly map to exactly one category in the allowed taxonomy, set flag=NEEDS_REVIEW and output category=Other. Do not output confident classifications when classification is genuinely ambiguous (e.g. complaint mentions both flooding and structural damage). Test: if reason contains hedging language (maybe, possibly, unclear) or description spans multiple unrelated categories, flag must be set."
  
  - "Failure Mode Prevention — Taxonomy Drift: Do not allow category names to vary across similar complaints. Test: run classifier.py on full test CSV; compare category assignments for similar complaints; confirm identical complaints receive identical categories."
  
  - "Failure Mode Prevention — False Confidence: Do not assign a category to ambiguous complaints. Test: identify complaints where keyword overlap exists between two or more categories; verify flag=NEEDS_REVIEW for these rows."
