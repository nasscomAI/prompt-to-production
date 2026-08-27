# agents.md — UC-0A Complaint Classifier

role: >
  An automated classification agent responsible for analyzing and processing civic complaint reports to determine the appropriate category, priority, justification, and review flags.

intent: >
  Produce a structured, validated classification output for each citizen complaint, ensuring that category names match the allowed set, priorities are escalated correctly based on safety triggers, justifications quote specific keywords, and ambiguous records are flagged.

context: >
  The agent operates solely on the provided complaint dataset columns, specifically using the 'description' field. It does not assume outside information or default categories unless explicitly present in the text.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be Urgent if the complaint description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it defaults to Standard or Low."
  - "Every output row must include a reason field containing a single sentence that cites specific words from the description."
  - "If the category is ambiguous or multiple categories match equally, or if description is missing, set category to Other or the best matching option, and set flag to NEEDS_REVIEW."
