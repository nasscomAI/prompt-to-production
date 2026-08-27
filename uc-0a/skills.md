# Skills to define in skills.md

name: classify_complaint
description: Classifies a single complaint row into category, priority, reason, and flag based on the defined schema
input:
  type: object
  format: "{ description: string }"
output:
  type: object
  format: "{ category: string, priority: string, reason: string, flag: string }"
error_handling: >
  If the description is missing or empty, return category as Other, priority as Low, reason indicating missing input, and flag as NEEDS_REVIEW; if category cannot be confidently mapped to one of the allowed values, set category to Other and flag as NEEDS_REVIEW; if ambiguity exists, do not guess and set flag as NEEDS_REVIEW; always ensure category matches exact allowed values and priority is set to Urgent if any severity keywords are present; if no justification can cite exact words from the description, flag as NEEDS_REVIEW

name: batch_classify
description: Processes an input CSV of complaints, applies classification to each row, and writes the results to an output CSV
input:
  type: object
  format: "{ input_csv_path: string, output_csv_path: string }"
output:
  type: file
  format: "CSV file with columns: category, priority, reason, flag"
error_handling: >
  If the input file is missing, unreadable, or not in CSV format, terminate with an error; if rows are malformed or missing descriptions, process them using classify_complaint error handling; ensure no extra or missing columns in output; if any classification produces invalid category or priority values, correct them to allowed values or flag as NEEDS_REVIEW; prevent taxonomy drift by enforcing exact category strings across all rows