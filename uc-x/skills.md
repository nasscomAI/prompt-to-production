skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes them by document name and section number.
    input: Paths to policy document text files.
    output: Structured index of documents and their sections.
    error_handling: If a document cannot be read or indexed, return NEEDS_REVIEW.

  - name: answer_question
    description: Searches indexed policy documents and returns a single-source answer with citation or the refusal template.
    input: User question and indexed policy documents.
    output: Answer with document name and section number citation, or the refusal template.
    error_handling: If the answer requires combining information from multiple documents, refuse using the refusal template.
