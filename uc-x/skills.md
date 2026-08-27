# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: Directory path containing the .txt policy documents.
    output: Dictionary mapping document names to dictionaries of section numbers and their text content.
    error_handling: Exits if documents are not found or cannot be parsed.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR the refusal template.
    input: User query string and the indexed document dictionary.
    output: Formatted string containing the exact citation OR the strict refusal template.
    error_handling: Explicitly defaults to the refusal template if the answer is ambiguous, missing, or requires cross-document blending.