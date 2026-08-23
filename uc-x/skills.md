# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes every numbered clause by document name and section number.
    input: Directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Index of entries {document, section (e.g. "3.1"), heading, clause_text}, one per numbered clause across all documents.
    error_handling: A missing or unreadable document exits non-zero naming the file; clauses that fail to parse are skipped from the index and counted in a warning rather than silently dropped.

  - name: answer_question
    description: Scores the question against the clause index and returns either a single-document answer with citations or the verbatim refusal template.
    input: str natural-language question; the clause index from retrieve_documents.
    output: str answer — quoted clause text with [document § section] citations, all from ONE document; OR the refusal template when coverage is absent or split across documents.
    error_handling: Zero/low keyword relevance returns the refusal template (never a guess); if two different documents score comparably, refuses instead of blending; malformed/empty questions return the refusal template; never raises to the interactive loop.
