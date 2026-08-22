skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes every clause by document name and section/clause number, plus a term-frequency index used for scoring questions against clauses.
    input: none (fixed set of 3 known policy file paths).
    output: list of clauses, each {doc_name, doc_ref, section_number, clause_number, text}, plus a document-frequency table over normalized tokens for scoring.
    error_handling: A policy file that fails to parse into any clauses raises loudly at startup rather than silently answering with 2 of 3 documents indexed.

  - name: answer_question
    description: Scores a question against every indexed clause (rarer shared words count for more), then answers from whichever single document scores highest — or refuses if no document clears the coverage threshold, or if two documents tie for the top score (genuine cross-document ambiguity).
    input: question (str), the indexed clauses and document-frequency table from retrieve_documents.
    output: str — either a citation-backed answer (document + clause numbers + clause text) drawn from exactly one document, or one of the two fixed refusal templates.
    error_handling: Empty/whitespace-only question → refusal template (nothing to score). Tied top score across documents → cross-document refusal naming both documents, never a blended answer.
