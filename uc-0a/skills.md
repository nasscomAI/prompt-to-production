- name: classify_complaint
  description: Classifies a single citizen complaint into a valid schema category and priority based on specific keywords and criteria.
  input:
  type: object
  format:
  description: string
  output:
  type: object
  format:
  category: string (Pothole | Flooding | Streetlight | Waste | Noise | Road Damage | Heritage Damage | Heat Hazard | Drain Blockage | Other)
  priority: string (Urgent | Standard | Low)
  reason: string (One sentence citing specific words from description)
  flag: string (NEEDS_REVIEW or blank)
  error_handling: Addresses core failure modes by strictly rejecting non-schema sub-categories to prevent taxonomy drift and hallucinated sub-categories, preventing severity blindness by forcing Urgent priority when severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present, requiring a specific citation in reason to avoid missing justification, and flagging genuine ambiguities as NEEDS_REVIEW instead of displaying false confidence.
- name: batch*classify
  description: Reads an input CSV file of citizen complaints, applies classify_complaint per row, and writes the structured classifications to an output CSV file.
  input:
  type: object
  format:
  input_filepath: string (e.g., ../data/city-test-files/test*[your-city].csv)
  output*filepath: string (e.g., uc-0a/results*[your-city].csv)
  output:
  type: object
  format:
  status: string
  processed_rows: integer
  output_filepath: string
  error_handling: Handles invalid file paths, missing columns, unreadable CSV data, or row-level classification failures by halting processing or flagging corrupt rows to prevent improper batch output writing.
