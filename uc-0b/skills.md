# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: >
      Load the policy .txt file and return a mapping from clause number
      (e.g., '2.3') to the exact clause text as it appears in the document.
    input: >
      input_path: string path to a .txt policy document.
    output: >
      dict mapping clause_number -> clause_text (string with normalized spacing).
    error_handling: >
      If a required clause number is missing, return an error object or raise a
      clear exception; do not fabricate clause text.

  - name: summarize_policy
    description: >
      Build the final summary by selecting the required clauses from the
      retrieved mapping and emitting a compliant summary that preserves all
      conditions.
    input: >
      policy_clauses: dict mapping clause_number -> clause_text.
    output: >
      A string representing summary_hr_leave.txt that contains all required clause
      numbers and their clause texts (verbatim/meaning-preserving).
    error_handling: >
      If any required clause is absent in policy_clauses, include a placeholder
      line noting the missing clause number and fail fast (never add invented content).
