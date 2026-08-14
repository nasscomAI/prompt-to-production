# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy .txt files and indexes them by document name and section number.
    input: A directory (or explicit paths) containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: >
      An index mapping each document name to its sections and clauses, where
      every clause is retrievable by its reference (e.g. "3.1") with its full
      text. Keeps documents separate — no merged corpus.
    error_handling: >
      If any of the three files is missing, it raises a clear error naming the
      missing file rather than answering from a partial corpus.

  - name: answer_question
    description: Answers a question from a single source document with citation, or returns the exact refusal template.
    input: the document index and a natural-language question (str).
    output: >
      Either a single-source answer string — the relevant clause text plus a
      citation "document_name § section" — or the verbatim refusal template.
      Never returns facts drawn from more than one document.
    error_handling: >
      When a question could only be answered by combining two documents, or is
      not covered at all (e.g. "flexible working culture"), it returns the
      refusal template unchanged instead of guessing or blending. No hedging
      phrases are ever emitted.
