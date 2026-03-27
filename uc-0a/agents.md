# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  [FILL IN: Who is this agent? What is its operational boundary?]

intent: >
  [FILL IN: What does a correct output look like — make it verifiable]

context: >
  [FILL IN: What information is the agent allowed to use? State exclusions explicitly.]

enforcement:
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - Priority must be exactly one of: Urgent, Standard, Low
  - Priority must be Urgent if any severity keyword is present in description — keywords are injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
  - Priority must not be Urgent if no severity keywords are present
  - Reason must be a single sentence
  - Reason must cite at least one specific word or phrase from the complaint description
  - Flag must be either NEEDS_REVIEW or blank — no other values
  - Flag must be set to NEEDS_REVIEW if category is genuinely ambiguous
  - Flag must not be set to NEEDS_REVIEW for complaints that map clearly to a single category
  - Category names must not vary or be modified from the allowed list
  - Valid classifications cannot output ambiguous categories with high confidence
