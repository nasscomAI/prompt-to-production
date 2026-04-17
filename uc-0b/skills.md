# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections for easier analysis.
    input: Path to a .txt policy file.
    output: A dictionary or list of structured sections (e.g., {"2.3": "content..."}).
    error_handling: Refuse if the file is not found or is not a text document.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all obligations and conditions.
    input: Structured policy sections and the ground truth clause inventory.
    output: A summary document with clause references.
    error_handling: If a section is missing from the summary, flag it as a critical failure.
