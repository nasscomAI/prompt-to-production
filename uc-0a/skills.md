# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
  description: Classifies a single citizen complaint into category, priority, reason, and flag fields based on strict schema rules.
  input:
    type: complaint row
    format: JSON or CSV row with fields [id, description]
  output:
    type: classification result
    format: JSON or table with fields [category, priority, reason, flag]
  error_handling: |
    If the description is ambiguous, set flag to NEEDS_REVIEW and leave category blank. 
    If category chosen is not in the allowed list, refuse and return an error. 
    If severity keywords are present but priority is not set to Urgent, correct and enforce Urgent. 
    Always require reason to cite specific words from description; if missing, return an error. 
    Refuse to invent sub-categories or vary category names.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input:
      type: file path
      format: CSV file with columns [id, description]
    output:
      type: file
      format: CSV file with columns [id, category, priority, reason, flag]
    error_handling: |
      If the input file is missing or malformed, return an error message. 
      If any row produces an invalid category or missing reason, flag the row and mark it for review. 
      If severity keywords are ignored, enforce Urgent priority. 
      If ambiguous complaints are classified with false confidence, set flag to NEEDS_REVIEW. 
      Ensure all category values match the allowed schema exactly.