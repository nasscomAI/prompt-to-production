skills:

- name: extract_leave_rules
  description: Extracts leave policy rules from a document.
  input: A leave policy document as text.
  output: A structured list of leave rules with conditions and approvals.
  error_handling: If a rule is unclear or incomplete, indicate that instead of guessing.

- name: validate_leave_rules
  description: Validates that extracted rules accurately match the source document.
  input: Original leave policy document and extracted rules.
  output: Validation result indicating whether the extracted rules are complete and accurate.
  error_handling: If required information is missing, return a validation error.
