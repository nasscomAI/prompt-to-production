skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes their numbered sections by document name and clause id.
    input: A list of policy document paths in plain text format.
    output: A structured index keyed by document name with numbered clauses and clause text.
    error_handling: Rejects missing files, unreadable content, or documents without numbered clauses instead of building a partial index silently.

  - name: answer_question
    description: Answers a policy question using one document source at a time and returns either a cited answer or the fixed refusal template.
    input: A user question string plus the indexed policy documents.
    output: A plain text answer that cites exactly one source document and section for each factual claim, or the refusal template when the answer is not covered.
    error_handling: Refuses when the answer would require blending multiple documents, when coverage is absent, or when the source is ambiguous.
