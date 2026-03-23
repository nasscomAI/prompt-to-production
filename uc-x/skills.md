# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of document file paths (List[str]).
    output: Indexed documents mapped by document name and section number (Dict).
    error_handling: If a document fails to load or is invalid, log the error and skip the document.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the exact refusal template.
    input: User question (str) and indexed documents (Dict).
    output: Factual single-source answer string with citation or the exact refusal template (str).
    error_handling: If an answer cannot be explicitly found in a single source, or is ambiguous across sources, return the refusal template.
