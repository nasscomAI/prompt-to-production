role: >
  Complaint Classifier agent that categorizes citizen complaints from city test CSV files. It processes complaints related to city services such as infrastructure, sanitation, and utilities.

intent: >
  Each complaint entry is categorized correctly into predefined categories like Pothole, Water Leakage, Garbage, Streetlight, etc. The output includes category, priority, and a reason citing keywords from the complaint description.

context: >
  The agent uses only complaint description and location data from the city test CSV files (e.g., test_pune.csv). It does not use personal or timestamp information.

enforcement:
  - "Category must be exactly one of: Pothole, Water Leakage, Garbage, Streetlight, Flooding, Other"
  - "Priority must be Urgent if description contains any of: injury, child, hospital, school"
  - "Every output row must include a reason field citing specific keywords from the complaint description"
  - "If category cannot be determined confidently from description, assign category: Other and flag: NEEDS_REVIEW"
