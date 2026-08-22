# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three available policy documents and indexes their numbered sections by document name and section number.
    input: Three policy document file paths in TXT format.
    output: Structured collection of documents containing document name, section number, and section text.
    error_handling: Reports a clear error if a required document is missing or cannot be read; does not substitute another source.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source grounded answer with document and section citations, or the exact refusal template.
    input: A user policy question as plain text plus the indexed policy documents.
    output: A concise answer whose factual claims cite one document and section, or the exact refusal template when the information is not covered or would require cross-document blending.
    error_handling: Refuses rather than guessing, blending documents, dropping conditions, or using unsupported information.