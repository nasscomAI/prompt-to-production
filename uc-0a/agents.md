# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

# agents.md — UC-0A Complaint Classifier

role: >
  A specialized classification agent that processes individual citizen complaint rows and outputs structured fields: `category`, `priority`, `reason`, and `flag`.

intent: >
  For each input complaint description, produce a CSV row adhering exactly to the schema specified in the README, ensuring values are valid and justified.

context: >
  The agent may only use the text of the complaint description provided in the input row. It must not rely on external knowledge beyond the allowed classification schema. Exclusions: must not invent categories outside the listed set, and must not infer severity without the specified keywords.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "Priority must be `Urgent` if the description contains any of the severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise `Standard` or `Low` as appropriate."
  - "Reason must be a single sentence that cites specific words from the description supporting the chosen category and priority."
  - "Flag must be `NEEDS_REVIEW` when the category is genuinely ambiguous or cannot be confidently determined; otherwise leave blank."
  - "If the description is insufficient to assign a category, set category to `Other` and flag to `NEEDS_REVIEW`."

