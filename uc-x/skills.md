# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files and indexes them by document name and
      section/clause number so answers can be traced to a single source.
    input: >
      A list of file paths to the three policy documents.
    output: >
      An index: for each document, an ordered list of clauses, each with the
      document name, clause number (e.g. "3.1"), section heading, and clause text.
    error_handling: >
      If a document cannot be opened, fail fast with a clear message naming the
      missing file. Lines without a clause number are attached to the current
      clause so no text is lost.

  - name: answer_question
    description: >
      Answers a natural-language question from a SINGLE best-matching document,
      returning the answer with a document + section citation, or the exact
      refusal template.
    input: >
      question (str), plus the index from retrieve_documents.
    output: >
      A string: either "According to <document> section <N.N>: <clause text>"
      (single source, single or multiple clauses from the SAME document), or the
      verbatim refusal template.
    error_handling: >
      Scores each document independently and selects only the single highest
      scoring document; never merges clauses from two documents. If the best
      score is below the relevance threshold, returns the refusal template with
      no hedging and no invented content.
