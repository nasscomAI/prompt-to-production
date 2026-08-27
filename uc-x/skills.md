skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: Path to the directory containing policy documents.
    output: A collection of indexed documents mapped by document name and section number.
    error_handling: Raises FileNotFoundError if any of the three required policy files are missing.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User question (String) and the collection of indexed documents.
    output: A factual answer from a single source with citation, or the exact refusal template.
    error_handling: Returns the refusal template if the answer requires blending documents, is not found, or is ambiguous.
