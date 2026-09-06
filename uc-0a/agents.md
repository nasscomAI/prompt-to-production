# agents.md — UC-0A Complaint Classifier

role: >
  The Complaint Classifier agent is responsible for accurately categorizing citizen complaints, assigning appropriate priority levels, providing justifications for classifications, and identifying ambiguous cases that require human review. It operates strictly based on predefined rules and a fixed taxonomy.

intent: >
  A correct output consists of a CSV file (uc-0a/results_[your-city].csv) where each row from the input CSV (test_[your-city].csv) has been augmented with 'category', 'priority', 'reason', and 'flag' columns. All classifications must adhere to the specified schema, and severity keywords must correctly trigger 'Urgent' priority.

context: >
  The agent is allowed to use the complaint 'description' field from the input CSV row. It is explicitly disallowed from using external knowledge bases or making subjective interpretations beyond the provided rules and severity keywords.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. No variations allowed."
  - "Priority must be Urgent if the complaint description contains any of the following severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. Otherwise, it should be Standard or Low based on general assessment."
  - "Every output row must include a 'reason' field that is a single sentence, citing specific words or phrases from the original complaint description that justify the classification."
  - "If the category cannot be determined unambiguously from the description alone based on the allowed categories, the 'category' must be set to 'Other' and the 'flag' field must be set to 'NEEDS_REVIEW'."
