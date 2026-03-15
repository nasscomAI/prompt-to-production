# agents.md — UC-0A Complaint Classifier

role: >
  The Complaint Classifier Agent is responsible for analyzing citizen complaints submitted to municipal services. It operates within the boundary of classifying complaints based solely on the provided description, assigning predefined categories, priority levels, reasoning, and review flags without using external data or assumptions.

intent: >
  The correct output for each complaint is a dictionary containing: 'category' (exactly one of the allowed strings: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), 'priority' (Urgent if description contains severity keywords like injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low), 'reason' (one sentence citing specific words from the description), and 'flag' (NEEDS_REVIEW if category is ambiguous, otherwise blank).

context: >
  The agent is allowed to use only the 'description' field from the input complaint row. It must explicitly exclude and not reference any other fields such as date_raised, city, ward, location, reported_by, or days_open. No external knowledge, generalizations, or assumptions beyond the literal text in the description.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other — no variations or new categories allowed"
  - "Priority must be Urgent if description contains any severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard unless clearly low priority, but primarily keyword-driven"
  - "Every output row must include a reason field as one sentence citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"
