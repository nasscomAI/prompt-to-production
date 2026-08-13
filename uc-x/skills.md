# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number.
    input: list of policy .txt paths
    output: dict — {doc_name: {sections: [{number, title}], clauses: [{number, text}]}}
    error_handling: Missing or unreadable file → clear error; empty or unparseable document → error; no clause ever blends into another document.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation OR the refusal template.
    input: question (str), document index (dict from retrieve_documents)
    output: str — answer prefixed with [document name | Section X.Y], or refusal template verbatim
    error_handling: No clause matches → refusal template exactly, no variations; best matches span two documents → refusal template (never blends); tie within one document → highest-scoring, lowest-numbered clause.
