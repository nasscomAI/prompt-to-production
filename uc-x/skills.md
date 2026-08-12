# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes every numbered clause by document name and clause number, with a per-clause word-frequency profile used for scoring.
    input: A list of the 3 fixed policy file paths (hr_leave, it_acceptable_use, finance_reimbursement).
    output: >
      A dict: document filename -> list of {section: str, text: str}
      (clause number and de-wrapped clause text), plus a corpus-wide term
      document-frequency table used by answer_question to down-weight
      generic words (e.g. "employee", "policy") and up-weight
      document-specific ones (e.g. "encashment", "MFA").
    error_handling: >
      If any of the 3 files is missing, raises a clear error naming which
      file is missing rather than silently answering from fewer sources
      (answering from 2 of 3 documents without saying so would itself be
      a silent-scope-reduction failure).

  - name: answer_question
    description: Scores a question's terms against every indexed clause, and returns either a single-source cited answer or the exact refusal template.
    input: question (str), the index from retrieve_documents.
    output: >
      A dict: {status: "answered"|"refused", source_document: str|None,
      sections: [str], text: str}. When answered, `text` is the cited
      clause(s) verbatim text from exactly one document. When refused,
      `text` is the exact refusal template.
    error_handling: >
      If the top-scoring document's best score is at or below a minimum
      relevance floor, refuses. If two different documents' best scores
      are within a narrow margin of each other (real cross-document
      ambiguity, e.g. the personal-phone/WFH question), refuses rather
      than guessing which one the user meant or blending both. Never
      raises an exception for a question it can't answer -- refusal is
      the defined, non-exceptional outcome for that case.
