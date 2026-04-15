# agents.md — UC-0A Complaint Classifier
# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.
# Delete these comments before committing.

role: >
  Act as a compliant classifier agent that classifies complaints into categories and priorities.

intent: >
  Given a list of complaint descriptions, verify and classify each item into `category`, `priority`, `reason`, and `flag` using only the text in the description.

context: >
  Use only the text provided in the complaint description. Exclude any external knowledge, inferred location data not explicitly stated, or assumptions about severity beyond the explicit text.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No synonyms, variations, or new categories are allowed."
  - "The 'priority' field values are: Urgent, Standard, Low. Set `Urgent` if any of these keywords are present: hospital, ambulance, fire, heat hazard, fell, collapse. Set `Standard` if any of these keywords are present: Injury, road, child, school, pothole, dark, flood. Set `Low` if any of these keywords are present: paving, heritage, waste, crater, music."
  - "The 'reason' field must be exactly one sentence and must cite specific words from the description."
  - "The 'flag' field must be set to NEEDS_REVIEW when the category is genuinely ambiguous; otherwise, leave it blank."
