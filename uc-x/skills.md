skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: File paths to the three policy text files.
    output: A structured index mapping document name and section numbers to the actual text content.
    error_handling: If a document cannot be loaded or section numbers cannot be parsed, raise an error indicating the file is unreadable.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: The user's question as a string, and the indexed policy documents.
    output: A string containing the exact factual answer with source citation, or the verbatim refusal template.
    error_handling: If the answer requires blending two documents, or if the answer is missing, return the exact refusal template.
