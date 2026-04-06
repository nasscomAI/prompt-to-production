- name: retrieve_policy
  description: Loads a policy document from a .txt file and returns its content as structured numbered sections.
  input:
    type: file
    format: .txt (e.g., policy_hr_leave.txt)
  output:
    type: structured text
    format: A list of numbered clauses with their corresponding obligations and binding verbs
  error_handling: If the input file is not found or the format is invalid, the skill returns an error message indicating the file could not be loaded.

- name: summarize_policy
  description: Takes structured sections of a policy document and produces a compliant summary with clause references.
  input:
    type: structured text
    format: A list of numbered clauses with corresponding obligations and binding verbs
  output:
    type: text
    format: A summarized policy document, with all 10 clauses and their full obligations and binding verbs intact
  error_handling: If the input does not match the expected format (e.g., missing clauses or incomplete obligations), the skill will return an error and flag the specific issues with the input.