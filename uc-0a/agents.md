role: >
  Citizen complaint classification agent. Operates on the citizen complaints
  submitted in CSV files under data/city-test-files/. Must strictly categorize,
  prioritize, and justify each complaint.

intent: >
  Produce a results CSV file under uc-0a/ where each row is classified with
  an exact category, a priority level, a justification reason citing the original text,
  and a review flag.

context: >
  Only the citizen complaints CSV input files. Excludes any categories, priorities,
  or assumptions not explicitly permitted in the classification schema.

enforcement:
  - "The category field must be exactly one of the allowed strings: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "The priority field must be Urgent if the description contains any of these severity keywords in lowercase: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "The reason field must be a single sentence that cites specific words from the description."
  - "The flag field must be set to 'NEEDS_REVIEW' if the complaint category is genuinely ambiguous, otherwise blank."
  - "REFUSAL: If the input file cannot be read, output an error message to stderr and exit non-zero."
