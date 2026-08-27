# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses the content into a structured format of numbered sections.
    input: type: string
format: file_path (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output: type: object
format: dictionary of numbered clauses mapping to their full text strings
    error_handling: If the file is missing, unreadable, or contains no identifiable numbered clauses, the skill returns a "FileAccessError" or an empty structure with a diagnostic flag.

  - name: summarize_policy
    description: Generates a summary of structured policy clauses while strictly preserving all conditions, binding verbs, and multi-condition obligations.
    input: type: object
format: structured dictionary of numbered clauses and their original text
    output: type: string
format: text summary including every numbered clause and explicit condition-level mapping
    error_handling: If a clause cannot be summarized without losing a condition or softening an obligation, the skill defaults to quoting the original text verbatim and appending a "PreservationFlag" to the output.
