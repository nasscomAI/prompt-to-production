# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy (.txt) file and transforms it into structured numbered sections for precise extraction.
    input: File path to a .txt policy document.
    output: A collection of structured sections, each with a clause number and its raw text content.
    error_handling: Return an error if the file format is incorrect or lacks numbered clause markers.

  - name: summarize_policy
    description: Generates a compliant summary from structured policy sections, ensuring all conditions and clauses are preserved as per enforcement rules.
    input: Object containing structured sections from retrieve_policy.
    output: A structured summary text where each clause is either summarized (preserving all conditions) or quoted verbatim with a flag.
    error_handling: Refuse and return an error if a multi-condition clause is detected but the summarization would result in a condition drop.
