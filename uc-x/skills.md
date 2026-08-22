# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and clause/section number, so lookups never need to guess which document a section number belongs to.
    input: list of 3 file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: >
      list of dicts, one per clause: {doc, clause, text} where doc is the
      source filename and clause is the "N.M" section number.
    error_handling: >
      If a file is missing, raises a clear error naming the missing file
      rather than silently indexing only the files that were found — a
      silently incomplete index would make single-source answers wrong
      without anyone noticing.

  - name: answer_question
    description: Searches the indexed documents for the single best-matching clause and returns either a single-source cited answer or the exact refusal template — by construction it can never blend two documents, because it always returns exactly one clause's text.
    input: index (from retrieve_documents), question (str).
    output: >
      dict {answer: str, doc: str or None, clause: str or None}. When a
      confident single-clause match is found, answer quotes that clause and
      doc/clause are populated for the citation. When no clause scores
      above the confidence threshold, answer is the exact refusal template
      and doc/clause are None.
    error_handling: >
      If the question is empty, returns the refusal template immediately
      without scoring anything.
