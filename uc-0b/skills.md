# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: Path to policy file (.txt); string.
    output: Structured list of sections with clause numbers and text.
    error_handling: Returns error if file missing, unreadable, or format invalid.

  - name: summarize_policy
    description: Takes structured sections and produces a summary with clause references, preserving all obligations and conditions.
    input: Structured list of sections; list of dicts.
    output: Summary text with clause numbers, compliant with enforcement rules.
    error_handling: Flags and quotes verbatim any clause that cannot be summarized without meaning loss; returns error if input is incomplete or ambiguous.
