# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
- name: classify_complaint
  description: Classifies a single citizen complaint row into predefined category, priority, reason, and flag fields.
  input: A single complaint row containing the complaint description text.
  output: A structure containing four fields (category, priority, reason, flag) that strictly align with the allowed schema values.
  error_handling: If the complaint category is genuinely ambiguous, set the flag to NEEDS_REVIEW to avoid false confidence; if severity keywords are present, set priority to Urgent to avoid severity blindness; strictly output only allowed categories to avoid hallucinated sub-categories.

- name: batch_classify
  description: Reads an input CSV of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
  input: An input CSV file path (e.g. ../data/city-test-files/test_hyderabad.csv).
  output: An output CSV file path (e.g. uc-0a/results_hyderabad.csv).
  error_handling: Validates that category names do not vary across rows for the same type of complaint to avoid taxonomy drift, and ensures all required fields are present in the final output before saving.