# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the HR policy document and returns structured numbered sections.
    input: Text file (.txt)
    output: Structured policy sections
    error_handling: Return an error if the policy file is missing or unreadable.

  - name: summarize_policy
    description: Generates a compliant summary while preserving all obligations and conditions.
    input: Structured policy sections
    output: Summary with clause references
    error_handling: Quote the clause instead of guessing when meaning may be lost.
