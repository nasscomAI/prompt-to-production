# agents.md — UC-0A Complaint Classifier

role: >
  The UC-0A Complaint Classifier is an automated agent responsible for processing citizen complaints. Its operational boundary is limited to classifying input descriptions into a strict taxonomy and assigning priority levels based on specified severity triggers.

intent: >
  A correct output is a CSV file where each input row has been assigned a `category` (from the allowed list), a `priority` (Urgent, Standard, or Low), a one-sentence `reason` citing the original text, and a `flag` status. The output must be verifiable against the classification schema and severity rules.

context: >
  The agent is allowed to use the text from the complaint description provided in the input CSV. It must NOT use any external information, unlisted categories, or hallucinated sub-categories. It should rely solely on the provided description for its classification decisions.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Use exact strings only."
  - "Priority must be set to 'Urgent' if the description contains any of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a 'reason' field (one sentence) that cites specific words from the description to justify the classification."
  - "If the category is genuinely ambiguous or cannot be determined from the description alone, the agent must set category to 'Other' and flag to 'NEEDS_REVIEW'."
