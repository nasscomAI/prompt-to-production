# skills.md — UC-X Policy Document Q&A

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number so answers can be grounded in a single, citable clause.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      An index: a list of clause entries, each
      {doc_key, doc_name, section (N.M), text, searchable}, where searchable is
      the section title plus clause text, normalised for matching. Clause text is
      preserved verbatim for quoting in answers.
    error_handling: >
      If any of the three files is missing/unreadable, fail loudly (raise) — a
      partial index would let a question be answered from an incomplete corpus.
      Banner/divider lines are ignored as decoration and never indexed as clauses.

  - name: answer_question
    description: Answers one question from a SINGLE best-matching clause with a citation, or returns the exact refusal template when nothing matches or the match would blend documents.
    input: >
      The index (from retrieve_documents) and a free-text question string.
    output: >
      Either a grounded answer — the verbatim clause text plus
      "Source: <document name>, section <N.M>" — or the refusal template verbatim.
      Exactly one document + one section per answer; never two.
    error_handling: >
      Score clauses by keyword overlap (light stemming; common words ignored;
      'phone/laptop' → device, 'slack/app' → software). If the best score is zero,
      return the refusal template (question not covered). If the top-scoring
      clauses span more than one document (a genuine cross-document tie), refuse
      rather than blend. On a within-document tie, pick the lowest section number.
      Never emit a hedging phrase and never answer without a citation.
