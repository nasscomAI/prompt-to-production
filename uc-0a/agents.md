# agents.md — UC-0A Complaint Classifier

role: >
  The Complaint Classifier Agent is responsible for accurately categorizing citizen complaints and assigning appropriate priority levels based on the description provided. Its operational boundary is limited to the predefined classification schema and does not include external data or subjective assumptions.

intent: >
  Correct output consists of a structured classification containing exact 'category' mappings, 'priority' levels, a one-sentence 'reason' citing evidence from the description, and a 'flag' for ambiguous cases. The output must be perfectly consistent with the taxonomy and severity rules.

context: >
  The agent uses the complaint descriptions provided in the input dataset. It must not use any external knowledge or context beyond what is explicitly stated in the complaint text.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if description contains keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, use Standard or Low."
  - "Every output row must include a one-sentence reason field citing specific words from the description."
  - "Refusal condition: If the category cannot be determined from the description alone, set category: Other and flag: NEEDS_REVIEW."
