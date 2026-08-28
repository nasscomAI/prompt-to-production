skills:
  - name: retrieve_documents
    description: Loads the three approved local policy documents and indexes each numbered clause by filename and section number.
    input: A policy-document directory path, or the default approved local directory.
    output: A mapping of document filename to section number to UTF-8 clause text.
    error_handling: Fails clearly if an approved document cannot be read; it does not substitute content from another source.

  - name: answer_question
    description: Searches indexed policy clauses and returns a single-document cited answer or the exact refusal template.
    input: A non-empty employee-policy question and the document-section index.
    output: Policy text with filename-and-section citations, or the exact required refusal text.
    error_handling: Returns the exact refusal template when support is absent, weak, ambiguous, or would require combining documents.
