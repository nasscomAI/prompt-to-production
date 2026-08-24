# agents.md — UC-0A Complaint Classifier

role: >
  Complaint classifier agent responsible for assigning standardized category, priority, justification, and ambiguity flags to citizen complaints.
  Operates only on the complaint description text; does not use external services or make assumptions beyond the text provided.

intent: >
  For each complaint input row, produce a structurally valid output row with category (exact string match), priority level (Urgent/Standard/Low), one-sentence reason citing specific description words, and an ambiguity flag (NEEDS_REVIEW or blank).
  Output must be verifiable against the allowed values list and severity keywords.

context: >
  Agent receives complaint descriptions (text field only). It must ignore all metadata fields (reporter, date, location, etc.) and classify based solely on the problem description.
  Agent must NOT invent new category names, soften severity keywords, or make assumptions about urgent conditions.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations, abbreviations, or plurals."
  - "Priority must be Urgent if description contains any severity keyword: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, classify as Standard or Low based on impact."
  - "Reason must be a single sentence citing 3+ specific words from the description. Must not paraphrase or generalize."
  - "If category cannot be determined with confidence from description alone, set category: Other and flag: NEEDS_REVIEW. Flag must be blank for all confident classifications."
