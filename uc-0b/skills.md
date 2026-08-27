# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text file and return structured numbered clauses
    input: file_path
    process:
      - Read the .txt policy document from the given path
      - Identify and extract numbered sections (e.g., 2.3, 2.4, 3.2)
      - Preserve exact clause text without modification
      - Return clauses as structured data with clause numbers as keys
    output: structured_clauses

  - name: summarize_policy
    description: Generate a clause-preserving summary without meaning loss
    input: structured_clauses
    process:
      - Iterate through each clause in structured_clauses
      - Produce a summary mapped to each clause number
      - Preserve all conditions, qualifiers, and thresholds
      - Ensure multi-condition clauses retain all components
      - Maintain original binding verbs (must, requires, will, not permitted)
      - Avoid adding external or assumed information
      - If a clause cannot be summarized without loss, include it verbatim and flag it
    output: compliant_summary