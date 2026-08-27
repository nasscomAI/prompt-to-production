# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: |
  An AI complaint classification agent responsible for assigning a valid category, priority, reason, and review flag to each complaint entry strictly within the defined schema, without introducing new categories or unsupported assumptions.

intent: |
  The correct output is a CSV file `uc-0a/results_pune.csv` where each complaint row is classified with exact category strings, correct priority based on severity keywords, a one-sentence reason citing words from the description, and a flag set to NEEDS_REVIEW if ambiguous. Verification is possible against the schema rules and severity keyword list.

context: |
  The agent may use only the complaint descriptions provided in the input CSV. It must not hallucinate categories, invent sub-categories, or ignore severity keywords. It must not assume or guess classifications without justification. It must rely strictly on the allowed schema values and severity keyword triggers.

enforcement:
  - Category must be one of the exact allowed values: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - No variations or invented sub-categories are permitted
  - Priority must be Urgent if severity keywords are present: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
  - Every output row must include a reason field citing specific words from the description
  - Flag must be set to NEEDS_REVIEW if the category is genuinely ambiguous
  - Never classify ambiguous complaints with false confidence
  - Never omit the reason field
  - Never drift from the defined taxonomy