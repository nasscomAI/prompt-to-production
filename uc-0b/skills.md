# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

    output: [What does it return? Type and format.]
  - name: retrieve_policy
    description: Loads the policy text file and converts it into structured numbered sections and clauses.
    input: A .txt policy file path.
    output: A list of sections, each containing a section number, section title, and ordered clause entries.
    error_handling: Raises an error if numbered clauses appear before a section heading or if the file cannot be read.
    output: [Type and format]
  - name: summarize_policy
    description: Produces a clause-preserving summary from structured policy sections with clause references.
    input: Structured numbered sections returned by retrieve_policy.
    output: A text summary that includes every clause reference and marks verbatim high-risk clauses.
    error_handling: Uses verbatim quoting for clauses where paraphrasing could drop conditions or change binding meaning.
