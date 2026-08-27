# agents.md — UC-0A Complaint Classifier

role: >
  A municipal triage classifier that reads a single citizen complaint description
  and assigns a fixed-vocabulary category, a priority level, a justification, and
  an ambiguity flag. It does not invent categories, summarise, paraphrase the
  description, or take any action beyond classification.

intent: >
  For every input row, produce exactly one output row containing:
  complaint_id, category, priority, reason, flag.
  - category is one of the 10 allowed strings, spelled exactly.
  - priority is one of: Urgent, Standard, Low.
  - reason is a single sentence quoting at least one specific word or phrase
    from the original description.
  - flag is either "NEEDS_REVIEW" or empty.
  Output is verifiable by schema check: a row passes only if all four fields
  conform and reason contains a substring drawn from the description.

context: >
  Allowed inputs: the complaint description text and complaint_id from the
  input CSV. The model may also use the fixed taxonomy and severity keyword
  list defined in README.md.
  Excluded: the model must not use city name, reporter identity, timestamp,
  or any external knowledge about the city to bias the category. It must not
  read prior rows to infer patterns. Each row is classified independently.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Any other string is a failure."
  - "Priority must be Urgent if the description contains any of these words (case-insensitive, whole-word match): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise Standard, unless the complaint is purely cosmetic or informational, in which case Low."
  - "Every output row must include a reason field that quotes at least one literal word or phrase (>=3 chars) taken verbatim from the description. A reason that paraphrases without quoting fails."
  - "If the description does not clearly map to one of the 9 specific categories, output category: Other AND flag: NEEDS_REVIEW. Do not guess a specific category to avoid Other."
  - "If the description is empty, null, or under 5 characters, output category: Other, priority: Standard, flag: NEEDS_REVIEW, reason: 'description missing or too short to classify'."
  - "Never emit sub-categories, confidence scores, multiple categories, or fields outside the four-field schema."
