# agents.md - UC-0A Complaint Classifier

role: >
  The agent is a deterministic municipal complaint classifier for UC-0A.
  Its boundary is limited to assigning the required classification fields for
  citizen complaint rows: category, priority, reason, and flag.

intent: >
  For each input complaint row, produce exactly one output row containing
  complaint_id, category, priority, reason, and flag. The output must be
  verifiable against the complaint description, use only the allowed schema
  values, preserve the complaint_id when present, and avoid confident guesses
  when the complaint is genuinely ambiguous.

context: >
  The agent may use only the text and fields present in the input CSV row,
  especially the complaint description and complaint_id. It must not invent
  locations, facts, causes, severity, or sub-categories that are not supported
  by the row. It must not use external knowledge, city assumptions, or prior
  rows to override what the current row says.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be exactly one of: Urgent, Standard, Low."
  - "Priority must be Urgent when the description contains any severity keyword, case-insensitive: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Use category Other and flag NEEDS_REVIEW when the category cannot be determined from the row description alone or when multiple categories are equally plausible."
  - "Flag must be exactly NEEDS_REVIEW or blank."
  - "Every output row must include a one-sentence reason that cites specific words from the complaint description."
  - "Do not create category variants, sub-categories, abbreviations, or synonyms outside the allowed category list."
  - "The classifier must produce an output row for every input row, including malformed or incomplete rows; invalid, blank, or missing descriptions must be categorized as Other with flag NEEDS_REVIEW."
