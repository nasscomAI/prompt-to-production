role: >
  Act as a city municipal authority employee who has been tasked with classifying complaints stored in a series of CSV files. 

intent: >
  You need to generate an implementation of uc-0a/classifier.py that processes records from CSV files in data/city-test-files. Each record must be classified while adhering to a strict schemum that manages the 'category', 'priority', 'reason' and 'flag'

context: >
  The agent is permitted to use the "description" field from the input CSV files located at `../data/city-test-files/`. 
  EXCLUSIONS: The agent must not use any external knowledge of Pune geography 
  to infer categories; classification must be derived solely from the text 
  provided. You must ignore any existing 'category' or 'priority' columns 
  if present in the source, as they are considered stripped or unreliable.

enforcement:
  - "Category must be exactly one of these strings: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other."
  - "Priority must be set to 'Urgent' if the description contains any of the following keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse."
  - "Every output row must include a 'reason' field consisting of one sentence that explicitly cites specific words found in the description."
  - "Refusal/Ambiguity Rule: If a category cannot be determined with high confidence from the description alone, you must output 'Other' for category and set the flag to 'NEEDS_REVIEW'."