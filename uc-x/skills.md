skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number so any clause can be traced to a single source.
    input: Paths to the three .txt policy documents.
    output: >
      An index of section groups, each tagged with its document name, section number,
      title, and ordered clauses (clause ref + full text), plus per-clause term
      statistics used for single-source retrieval.
    error_handling: >
      If any document is missing or unreadable, raise a clear error naming the file and
      stop; it does not answer from a partial set of documents.

  - name: answer_question
    description: Answers a question from exactly one document's most relevant section group with citations, or returns the exact refusal template.
    input: The document index and a free-text question.
    output: >
      Either the relevant clause(s) from a single document, each cited as
      'filename § section', or the verbatim refusal template when no single document
      distinctively covers the question.
    error_handling: >
      Refuses (returns the refusal template) when no distinctive match exists rather
      than hedging or guessing. Never blends two documents. Never emits banned hedging
      phrases. Preserves every condition of a matched clause.
