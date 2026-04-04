# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns content as structured numbered sections.
    input: File path (string)
    output: A collection of numbered clauses with their text (dictionary or list).
    error_handling: Raises an error if the file cannot be accessed or is malformed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary maintaining all conditions and rules.
    input: Structured clauses (dictionary or list)
    output: A strict summary string adhering to the enforcement rules.
    error_handling: Refuses generation if multi-condition obligations cannot be fully preserved.
