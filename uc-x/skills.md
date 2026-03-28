skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number.
    input: List of file paths to policy txt files.
    output: A nested dictionary mapping document names -> section numbers -> exact text.
    error_handling: Handles missing policy files safely.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template.
    input: User's question string and the indexed documents dictionary.
    output: A single formatted string containing the answer and citation, or the exact refusal template.
    error_handling: Safely ejects using the strict refusal template if a question spans multiple documents or cannot be resolved.
