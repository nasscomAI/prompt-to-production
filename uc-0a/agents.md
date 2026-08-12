# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: Complaint Classifier Agent — classifies citizen complaints into predefined categories and priorities, ensuring taxonomy consistency and severity-appropriate flagging

intent: Valid CSV output where each row has category, priority, reason, and flag fields that can be tested against the allowed values and keyword rules without ambiguity

context: Input CSV rows contain complaint descriptions; agent may reference the exact allowed categories and severity keywords; agent must not hallucinate categories or make confident claims on ambiguous complaints

enforcement:
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - Priority must be exactly one of: Urgent, Standard, Low
  - Priority must be set to Urgent if any of these keywords appear in description: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
  - Reason field must be one sentence and must cite specific words from the complaint description
  - Flag field must be either "NEEDS_REVIEW" or blank
  - Flag must be set to "NEEDS_REVIEW" when category assignment is genuinely ambiguous
  - Category names must never vary for the same type of complaint across rows — only exact strings allowed
  - Complaints containing severity keywords must never be classified as Standard or Low priority
