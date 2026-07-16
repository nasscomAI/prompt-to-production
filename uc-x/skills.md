skills:
  - name: retrieve_documents
    description: >
      Load all 3 policy .txt files and index them by document name and
      section number, storing the raw text for full-text search.
    input: >
      doc_paths (dict) — mapping of short names to file paths for the 3 policy documents
    output: >
      dict — document names mapped to their full text content
    error_handling: >
      If any file is missing or unreadable, raise FileNotFoundError with the
      missing file path. All documents must load successfully or none are returned.

  - name: answer_question
    description: >
      Search across all indexed documents for the user's question and return
      a single-source answer with citations, or the refusal template if not found.
    input: >
      question (str), documents (dict of doc_name -> text)
    output: >
      str — either a cited answer from one document, or the verbatim refusal template
    error_handling: >
      If the question matches content in multiple documents, return the refusal template
      (single-source violation). Never blend answers. Never hedge or paraphrase the refusal.
