# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the policy document and structures it into numbered clauses.
    input: Path to a .txt policy file (string)
    output: List of structured clauses (e.g., [{"clause": "2.3", "text": "..."}])
    error_handling: >
      If the file is missing, unreadable, or not properly formatted, return an error message
      indicating invalid input and stop execution.

  - name: summarize_policy
    description: Generates a clause-preserving summary of the policy document.
    input: List of structured clauses with clause numbers and text
    output: Text summary where each clause is represented with preserved obligations and conditions
    error_handling: >
      If a clause is ambiguous or cannot be summarized without losing meaning,
      include the original clause verbatim and mark it as [REQUIRES REVIEW].