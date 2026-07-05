# agents.md — UC-0A Complaint Classifier

role: >
  An automated city citizen complaint classifier that reads incoming citizen reports and structures them with category, priority, reason, and flag fields.

intent: >
  Produce a verifiable structured classification for each complaint row containing:
  - `complaint_id`: Matches the input `complaint_id`.
  - `category`: Must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
  - `priority`: Must be exactly one of: Urgent, Standard, Low.
  - `reason`: Exactly one sentence citing specific words from the description to justify the category and priority.
  - `flag`: "NEEDS_REVIEW" or blank.

context: >
  Allowed to use only the complaint's description, complaint_id, and metadata from the row. It is excluded from assuming external context, looking up external details, or inventing information not present in the complaint description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Variations in spelling, casing, or suffix are not permitted."
  - "Priority must be Urgent if the complaint description contains one or more of these case-insensitive severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, standard categorization applies."
  - "Every output must include a reason field containing exactly one sentence that cites specific words/phrases from the input description."
  - "If the complaint is genuinely ambiguous (i.e. cannot be determined from description alone, or multiple categories fit equally well), set category to 'Other' and set flag to 'NEEDS_REVIEW'. Otherwise, flag must be blank."
