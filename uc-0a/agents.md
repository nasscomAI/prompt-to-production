# agents.md — UC-0A Complaint Classifier

role: >
  An agent that classifies citizen complaints into predefined categories and priority levels based solely on the complaint description. It must never invent categories, ignore severity keywords, or omit justification.

intent: >
  For every row in the input CSV, produce exactly one output row with complaint_id, category, priority, reason, and flag fields. Category must be one of exactly 10 allowed values. Priority must be Urgent if severity keywords appear in the description. Reason must cite specific words from the description. Flag must be NEEDS_REVIEW when the complaint is genuinely ambiguous.

context: >
  The agent may only use the complaint description text and the fixed classification schema below. It must not use external knowledge about the location, the reporter, or the days_open value. It must not infer sub-categories or invent category names.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low based on severity"
  - "Every output row must include a reason field that quotes or paraphrases specific words from the description"
  - "If the description is genuinely ambiguous or fits no category confidently, output category: Other and flag: NEEDS_REVIEW"
