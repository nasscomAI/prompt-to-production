skills:
  - name: retrieve_documents
    description: Loads the three policy text files, parses them into sections, and indexes them by document name and section number.
    input: Paths to the three policy files as strings.
    output: A dictionary mapping document names to dictionaries mapping section numbers (e.g. '2.6', '3.1') to their raw text content.
    error_handling: If any of the files are missing, raises FileNotFoundError.

  - name: answer_question
    description: Searches the indexed document sections to answer the user's question, ensuring a single-source answer with proper citation or a clean refusal.
    input: The user's question as a string, and the indexed sections dictionary.
    output: A string containing the answer and citation, or the exact refusal template with dynamic team contact details.
    error_handling: Returns the exact refusal template if the query does not match any indexed section with high confidence, or if it would cause cross-document blending.
