skills:

- name: classify_complaint
  description: This skill reads a citizen complaint and classifies it into a service category.
  inputs: complaint_text (string)
  outputs: category (sanitation, water, roads, other)
  error_handling: If complaint text is empty or unclear, return category "other".

- name: keyword_detection
  description: Detects important keywords in the complaint text to help classification.
  inputs: complaint_text (string)
  outputs: detected_keyword (string)
  error_handling: If no keyword is detected, return "none".