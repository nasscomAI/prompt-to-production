skills:
  - name: retrieve_documents
    description: Loads all policy text files and parses/indexes them by document name and section number.
    input:
      type: list
      format: A list of file paths to the policy text files.
    output:
      type: dict
      format: A nested dictionary mapping document names and section numbers to raw text.
    error_handling: Logs a warning and continues if one of the files cannot be found or read.

  - name: answer_question
    description: Searches the indexed documents and generates a single-source cited answer or returns the refusal template.
    input:
      type: str
      format: The user's question text.
    output:
      type: str
      format: The cited answer text or the refusal template.
    error_handling: Returns the refusal template if the query is ambiguous, empty, or not found.
