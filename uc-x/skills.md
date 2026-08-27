skills:
  - name: retrieve_documents
    description: >
      Load all 3 policy .txt files, parse them into structured
      sections and numbered clauses, and return an index keyed by
      keywords and section numbers for lookup.
    input: >
      List of 3 file paths to policy .txt files.
    output: >
      Dict with documents keyed by filename; each document has
      sections with headings and clause lists.
    error_handling: >
      If any file is missing or unreadable, raise FileNotFoundError
      with the missing path.

  - name: answer_question
    description: >
      Given a question and the document index, find the single best
      matching clause from a single document. If matches span
      multiple documents, refuse. If no match, use refusal template.
      Return answer with citation.
    input: >
      String question, dict document_index.
    output: >
      String answer with source citation, or the refusal template
      if no single-document match found.
    error_handling: >
      If question matches multiple documents, return the refusal
      template (do not blend). If ambiguous, prefer refusal over
      hallucination.
