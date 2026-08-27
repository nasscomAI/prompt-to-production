skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes each clause by document name and section number.
    input: A mapping of document names to file paths.
    output: A searchable in-memory index of policy clauses.
    error_handling: Raise a clear error if any required file is missing or cannot be parsed into numbered clauses.

  - name: answer_question
    description: Matches a user question to one policy clause or returns the refusal template when the answer is not covered.
    input: A natural-language question string and the indexed policy clauses.
    output: A single-source answer with citation or the exact refusal template.
    error_handling: Refuse if the question is uncovered, ambiguous across documents, or would require blending multiple documents.
