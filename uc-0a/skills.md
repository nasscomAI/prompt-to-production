# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: complaint_category_classification
    description: Classifies a complaint description into exactly one allowed category using strict rule-based matching.
    input: Plain text string containing the complaint description.
    output: One category from the allowed list (Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other).
    error_handling: If the description does not clearly match any category, returns "Other" and sets flag to NEEDS_REVIEW.

  - name: priority_assignment
    description: Determines complaint priority based on presence of predefined urgency keywords.
    input: Plain text string containing the complaint description.
    output: One of Urgent, Standard, or Low.
    error_handling: If input is empty or unclear, defaults to Standard unless urgency keywords are explicitly present.
