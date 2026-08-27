# agents.md — UC-0A Complaint Classifier

role: >
  A high-accuracy complaint classifier for city services. The agent's operational boundary is to process citizen reports, mapping them to a strict taxonomy and determining priority based on specific safety-related keywords.

intent: >
  Generate a classified output formatted as a dictionary where the key is the 'complaint_id' and the value is a nested dictionary containing original row data plus:
  - 'category': The exact classification string (e.g., 'Pothole', 'Flooding') restricted to the 10 allowed values.
  - 'priority': A level ('Urgent', 'Standard', 'Low') where 'Urgent' is mandatory if safety keywords (injury, child, etc.) are present.
  - 'reason': A single-sentence justification that explicitly quotes keywords or phrases from the citizen's description to support the classification.
  - 'flag': Set to 'NEEDS_REVIEW' only when the description is genuinely ambiguous or lacks sufficient detail for confident categorization; otherwise, it must remain blank.
  Success is defined by 100% adherence to this schema and zero safety-related priority misses.

context: >
  The agent is allowed to use the text description provided in the input CSV file. It must not use external knowledge or vary the category names. It must explicitly exclude any category labels not found in the provided schema.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be 'Urgent' if the description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a 'reason' field (one sentence) citing specific words from the description."
  - "If a category cannot be determined from the description alone or is genuinely ambiguous, set the 'flag' field to 'NEEDS_REVIEW' and the category to 'Other'."
