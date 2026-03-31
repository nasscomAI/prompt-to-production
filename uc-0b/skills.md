# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses it into structured numbered sections for precise analysis.
    input: File path to a .txt policy document.
    output: A list of objects, each containing a clause number and its raw text content.
    error_handling: Reports an error if the file is inaccessible or lacks a numbering system.

  - name: summarize_policy
    description: Summarizes structured policy sections into concise bullet points, preserving all mandatory conditions and clause references.
    input: List of structured policy sections.
    output: A summary string where every point references a source clause and retains all binding obligations.
    error_handling: Quotes problematic clauses verbatim and flags them if a safe summary is impossible.
