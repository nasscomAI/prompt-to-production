# skills.md
# UC-0B skill definitions

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns structured sections with clause numbers.
    input: path string (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: JSON object with "clauses": array of {"number", "text"}, and metadata fields.
    error_handling: If file missing or unreadable, raise an explicit error. If parsing fails, return a validation error with line context.

  - name: summarize_policy
    description: Takes structured policy clauses and returns a compliant summary preserving clause-level meaning.
    input: structured clauses from retrieve_policy, plus optional template options.
    output: text summary with each clause mapped and conditions preserved. include clause references.
    error_handling: If required clause(s) are missing, return a refusal reason. If summarization would drop conditions, return the verbatim clause with a warning.

