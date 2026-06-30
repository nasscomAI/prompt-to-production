# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes them by document name and section/clause number.
    input: >
      paths (list[str]) — the HR leave, IT acceptable-use, and finance
      reimbursement policy files. Each has numbered sections ("3. PERSONAL
      DEVICES (BYOD)") and numbered clauses ("3.1 ...").
    output: >
      A flat index of clauses, each {doc_name, doc_ref, section, section_title,
      clause_id, text}, plus an inverse-document-frequency table over clause
      tokens used for scoring. Every clause is traceable to one document.
    error_handling: >
      A missing or unreadable file raises a clear error naming the path.
      Continuation lines are folded into their clause so no source text is lost.

  - name: answer_question
    description: Returns a single-source cited answer for a question, or the exact refusal template — never a blend.
    input: >
      question (str) and the index from retrieve_documents.
    output: >
      Either a string containing the citation [doc_name · Section X.Y] followed by
      the verbatim governing clause, OR the fixed refusal template. Exactly one
      clause is ever returned; answers from two documents are never concatenated.
    error_handling: >
      If no single clause clears the relevance threshold, return the refusal
      template verbatim rather than guessing or hedging. Ties or weak matches
      resolve to refusal, not to a blended answer.
