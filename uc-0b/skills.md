# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: Path to a .txt policy file (string).
    output: Structured data with numbered sections (e.g., list or dict with section numbers and text).
    error_handling: Returns an error if the file is missing, unreadable, or not in expected format; flags ambiguous or unnumbered sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a summary that preserves all obligations and clause references.
    input: Structured policy sections (list or dict as output by retrieve_policy).
    output: Summary text with clause references, compliant with enforcement rules.
    error_handling: Flags and quotes any clause that cannot be summarized without loss of meaning; returns error if input structure is invalid or incomplete.
