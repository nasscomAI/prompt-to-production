# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all policy documents and indexes them by document name and section number for searchable retrieval.
    input: >
      A directory path (string) containing the policy .txt files, or a list of
      specific file paths.
    output: >
      A dictionary with keys:
      - documents: dict mapping document_name to dict with 'metadata' and 'sections'
      - section_index: dict mapping "document_name:section_number" to section content
      - search_keywords: dict mapping common terms to relevant sections
    error_handling: >
      If directory/files not found: raise FileNotFoundError.
      If a file fails to parse: log warning but continue with other files.
      Return partial results if some files load successfully.

  - name: answer_question
    description: Searches indexed documents for relevant sections and returns a single-source answer with citation or the refusal template.
    input: >
      Dictionary with keys:
      - question: string (the user's question)
      - documents: the indexed documents from retrieve_documents
    output: >
      Dictionary with keys:
      - answer: string (the response text)
      - source: string (document name + section number) or 'NOT_FOUND'
      - confidence: string ('HIGH' if exact match, 'MEDIUM' if inference needed, 'REFUSED' if not found)
    error_handling: >
      If question matches multiple documents equally: DO NOT BLEND. Either pick
      the most specific source or use refusal template if genuinely ambiguous.
      If question is not covered: return the exact refusal template, no variations.
      Never hedge with phrases like "while not explicitly covered".
