# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Reads a policy document and extracts numbered clauses.
    input: Text file path.
    output: Ordered policy clauses.
    error_handling: Raise an error if the file cannot be read.

  - name: summarize_policy
    description: Produces a clause-preserving summary.
    input: Ordered policy clauses.
    output: Summary with clause references.
    error_handling: Quote any clause that cannot be summarized safely.
