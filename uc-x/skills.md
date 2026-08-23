skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and parses/indexes them by document name and section number.
    input: None.
    output: A dictionary mapping document filenames to their full text content.
    error_handling: Raises FileNotFoundError if any of the three required policy text files are missing.

  - name: answer_question
    description: Uses Gemini model to search the indexed policies and returns a single-source answer with section citation, or outputs the verbatim refusal template.
    input: documents (dict) - mapping of doc names to content, question (str) - the user query.
    output: An answer or refusal message (str).
    error_handling: Falls back to the refusal template if the LLM call fails or the query is out-of-scope.
