# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [classify_complaint]
    description: [Classifies a single citizen complaint row into a strictly defined category, priority level, one-sentence reason, and review flag.]
    input: [Object or dictionary containing the raw complaint row data, primarily the text description.]
    output: [Object or dictionary containing the exact category string, priority level, one-sentence reason citing the description, and an optional review flag.]
    error_handling: [Sets flag to NEEDS_REVIEW when the category is genuinely ambiguous instead of having false confidence; strictly uses only allowed category names without hallucinating sub-categories; enforces Urgent priority if severity keywords are present to prevent severity blindness; requires a one-sentence reason explicitly citing the text to avoid missing justification.]

  - name: [batch_classify]
    description: [Reads an input CSV file of citizen complaints, applies row-by-row classification, and writes the categorizations to an output CSV.]
    input: [String file path to an input CSV formatted with 15 stripped complaint rows per city.]
    output: [String file path to the resulting output CSV containing the fully classified rows.]
    error_handling: [Systematically verifies that exactly the allowed category names are used across all rows to prevent taxonomy drift; halts and logs an error if the input file format is invalid or missing; ensures every output row strictly complies with the classification schema and does not suffer from severity blindness or missing justification.]
