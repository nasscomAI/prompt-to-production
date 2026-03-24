skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its contents as structured, numbered sections for precise extraction.
    input: File path to a raw text policy document (e.g., .txt format).
    output: A structured text representation where each clause is individually numbered and separated from the others.
    error_handling: Return an error message requiring manual review if the file is unreadable, missing, or fails to parse into discrete logical clauses.

  - name: summarize_policy
    description: Synthesizes structured policy sections into a high-fidelity summary capturing all required core clauses without condition dropping or adding external context.
    input: Structured, numbered sections from a leave policy document.
    output: A precise text summary explicitly referencing all required source clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) and preserving multi-condition obligations.
    error_handling: Quote a clause verbatim and flag it for manual review if it cannot be summarized without losing multi-condition obligations or original meaning.
