skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None required.
    output: Indexed policy documents mapped by document name and section number.
    error_handling: Raise an error if any of the three policy files are missing or cannot be read.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation or the exact refusal template.
    input: The user's question as a string.
    output: A precise verbal answer including the source document name and section number, or the exact refusal template.
    error_handling: Return the exact refusal template without variations if the answer is not found, is ambiguous, or requires blending multiple documents.
