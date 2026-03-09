skills:
  - name: retrieve_documents
    description: Loads and indexes the three policy TXT files by document name and section number for deterministic lookups.
    input: List of file paths.
    output: A structured dictionary/index of all document sections.
    error_handling: Raise error if any of the three required documents are missing.

  - name: answer_question
    description: Searches the indexed documents for a query and returns a single-source answer with citations or the refusal template.
    input: Query string and indexed documents.
    output: A string containing the cited answer or the refusal template.
    error_handling: If no documents contain the answer, return the refusal template. If multiple documents match and create a "blend" risk, prioritize the most technical/specific source or refuse.
