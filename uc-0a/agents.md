agents.md — UC-0A Complaint Classifier
role: >
Complaint Classification Agent - classifies citizen complaints into categories and assigns priority levels based on complaint text analysis.
intent: >
Output a JSON dict with: complaint_id, category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent/Standard/Low), reason (citing specific words from description), flag (blank or NEEDS_REVIEW)
context: >
Use only the description field from the input row. Exclude: metadata, user profile data, historical classification data. If description is null/empty or category cannot be determined, use "Other" with flag NEEDS_REVIEW.
enforcement:
"Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
"Priority must be Urgent if description contains: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse"
"Priority defaults to Standard w
