# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: a mapping of {document_name: file_path} (defaults to the 3 policy files).
    output: >
      A list of clause records {doc, section, title, text, tokens} (each clause
      carries its section-header context) plus an IDF table over clause token-sets
      for relevance scoring.
    error_handling: >
      Skips blank/divider lines; rejoins wrapped clause lines. A missing/unreadable
      file surfaces as a load error rather than a silent empty index.

  - name: answer_question
    description: Return a single-source answer with citation, or the verbatim refusal template.
    input: a question string plus the indexed clauses and IDF table.
    output: >
      A dict {answer, source_document, section, excerpt, refused}. When answered,
      answer is the full source clause (conditions intact), with document + section
      and a ≤125-char excerpt. When refused, answer is the exact refusal template.
    error_handling: >
      Scores clauses across ALL documents and returns only the single best one
      (no blending). If no clause clears the confidence threshold / 2-term minimum
      (and no distinctive-term boost applies), it returns the refusal template.
