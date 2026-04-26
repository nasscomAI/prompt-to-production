# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: File path to the policy document (String).
    output: Structured document content divided into numbered sections.
    error_handling: Returns an error message if the file is missing, unreadable, or improperly formatted.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary with correct clause references.
    input: Structured numbered sections from the policy document.
    output: A meaning-preserving summary of the policy (String).
    error_handling: Flags verbatim quotes if a clause cannot be summarized without losing meaning or dropping conditions.
