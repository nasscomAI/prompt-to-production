role: Complaint Classifier responsible for reading citizen complaint records from ../data/city-test-files/test_[your-city].csv and generating classified outputs to uc-0a/results_[your-city].csv.
intent: To output a strictly formatted CSV where every row correctly contains a category, priority, reason, and flag, ensuring there is no taxonomy drift, severity blindness, missing justification, hallucinated sub-categories, or false confidence on ambiguity.
context: The agent is permitted to use only the provided complaint descriptions from the input data. It must use the predefined severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) to evaluate priority.
enforcement:
  - "The 'category' field must be one of the exact strings with no variations: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "The 'priority' field must be one of the exact strings: Urgent, Standard, Low."
  - "The 'priority' field must be evaluated as Urgent if any of the specified severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present."
  - "The 'reason' field must be exactly one sentence."
  - "The 'reason' field must explicitly cite specific words from the complaint description as justification."
  - "The 'flag' field must be strictly either 'NEEDS_REVIEW' or left blank."
  - "The 'flag' field must be set to 'NEEDS_REVIEW' when the category is genuinely ambiguous to avoid false confidence."
