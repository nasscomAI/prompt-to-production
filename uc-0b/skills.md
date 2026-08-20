# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: Path to policy text file (string).
    output: List of sections, each with clause number, core obligation, and binding verb (structured data).
    error_handling: If file is missing or unreadable, returns an error message and empty list.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: List of structured sections (as above).
    output: Text summary with all clauses present, multi-condition obligations preserved, and verbatim quotes flagged if summarization would lose meaning.
    error_handling: If input is incomplete or ambiguous, outputs a warning and includes verbatim quotes for affected clauses.
