skills:
  - name: retrieve_documents
    description: Reads the three policy documents and parses them into an index keyed by document name and section/clause number.
    input: None (or paths to the three files).
    output: A dictionary representing parsed sections and clauses from all three documents.
    error_handling: Logs warning messages or raises exceptions if any of the files are missing.

  - name: answer_question
    description: Takes an user query, matches it against the document index, and returns either a cited single-source answer or the exact refusal template.
    input: A string query.
    output: A string containing the answer with citation, or the exact refusal template.
    error_handling: Returns the exact refusal template if no matching clauses meet the similarity threshold.
