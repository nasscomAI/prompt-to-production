# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name
      and section number for retrieval.
    input: Optional directory containing policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt
      (defaults to ../data/policy-documents relative to app.py).
    output: Index mapping each document name to an ordered list of sections
      {number, text, heading}; clauses are keyed by their N.N number.
    error_handling: A missing or unreadable document exits cleanly with an
      ERROR naming the file (exit 1) rather than answering from a partial
      corpus; documents with no numbered clauses produce an empty index that
      forces refusals instead of hallucinated answers.

  - name: answer_question
    description: Searches the indexed documents and returns either a
      single-source answer with citations or the exact refusal template.
    input: A natural-language question string plus the index produced by
      retrieve_documents.
    output: Answer text quoting the best-matching section(s) of ONE document
      with [document | Section N.N] citations and a source-citation footer;
      or the exact three-line refusal template with [relevant team]
      substituted when the question is uncovered or two documents compete as
      sources.
    error_handling: Empty/whitespace questions return the refusal template.
      If the best score is below the coverage threshold, or the top two scores
      come from DIFFERENT documents within a blend-risk ratio, it refuses
      instead of blending. Supporting sections are only ever added from the
      SAME document as the primary citation; hedging phrases are banned by
      construction and checked at output time.
