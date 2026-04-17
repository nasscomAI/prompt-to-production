# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: file_path (string)
    output: A list of dicts with keys — clause_number, content
    error_handling: If file not found, raise FileNotFoundError.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: A list of dicts with keys — clause_number, content
    output: A string containing the formatted summary
    error_handling: If a section is missing its clause number, flag it for manual review.
