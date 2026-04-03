# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: >
      Reads a policy text file and extracts structured numbered clauses.
    input: file_path
    output: structured_clauses
    steps:
      - Open the text file
      - Identify numbered sections (e.g., 2.3, 2.4, etc.)
      - Store each clause with its content

  - name: summarize_policy
    description: >
      Generates a compliant summary ensuring no clause omission or meaning change.
    input: structured_clauses
    output: summary_text
    steps:
      - Iterate through each clause
      - Preserve all obligations and binding verbs
      - Ensure multi-condition clauses retain all conditions
      - If summarization risks meaning loss, quote verbatim
      - Output structured summary with clause references