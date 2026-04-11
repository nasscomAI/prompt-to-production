# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into predefined categories with appropriate priority and justification.
    input: A dict object with the following fields:
  - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - priority: Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard
  - reason: one sentence explaining the classification, citing specific words from the description
  - flag: NEEDS_REVIEW if category is ambiguous, otherwise blank
    output: A dict object with the following fields:
  - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - priority: Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard
  - reason: one sentence explaining the classification, citing specific words from the description
  - flag: NEEDS_REVIEW if category is ambiguous, otherwise blank
    error_handling: [What does it do when input is invalid or ambiguous?]

  - name: batch_classify
    description: Reads a CSV file containing citizen complaints and classifies each complaint using the classify_complaint skill.
    input: A CSV file with the following columns:
  - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - priority: Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard
  - reason: one sentence explaining the classification, citing specific words from the description
  - flag: NEEDS_REVIEW if category is ambiguous, otherwise blank
    output: A CSV file with the following columns:
  - category: one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - priority: Urgent if description contains injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard
  - reason: one sentence explaining the classification, citing specific words from the description
  - flag: NEEDS_REVIEW if category is ambiguous, otherwise blank
    error_handling: If the input CSV file is empty or contains invalid data, return an error message indicating the issue.
