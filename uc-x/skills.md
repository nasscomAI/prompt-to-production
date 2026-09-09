skills:
  - name: retrieve_documents
    description: Loads all three policy documents and indexes their content by document name and section number.
    input: Three policy text files in .txt format.
    output: Structured policy sections indexed by document name and section number.
    error_handling: If a document is missing, unreadable, or cannot be indexed, report the error and do not guess or create information.

  - name: answer_question
    description: Answers a staff question using a single policy document source or returns the required refusal template.
    input: A staff question and the indexed policy documents.
    output: An answer supported by one policy document with document name and section citation, or the exact refusal template.
    error_handling: Never combine claims from different documents, never hedge, and use the exact refusal template when the question is not covered or cannot be safely answered from one document.