# skills.md — UC-X Ask My Documents Agent

skills:
  - name: retrieve_documents
    description: Loads the three policy .txt files and indexes every clause by document name and section number.
    input: Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt (UTF-8 plain text, clauses numbered "X.Y").
    output: An index of entries {document: str, section: str, clause_id: str, text: str} in document order — e.g. {document: "policy_it_acceptable_use.txt", section: "3", clause_id: "3.1", text: "Personal devices may be used to access CMC email..."}.
    error_handling: Missing or unreadable files abort startup with an explicit error naming the file; unparsable lines are retained under their section rather than dropped so no source text is lost.

  - name: answer_question
    description: Searches the indexed documents for a single best-matching clause and returns a cited single-source answer or the exact refusal template.
    input: The index from retrieve_documents plus a question string (e.g. "Who approves leave without pay?").
    output: Either an answer quoting the matched clause with one citation "[document § X.Y]" from exactly ONE document, or the refusal template verbatim when no document covers the question or top matches conflict across documents.
    error_handling: Never blends claims from two documents; never emits hedged text ("while not explicitly covered...", "typically"); if retrieval confidence is low or cross-document matches tie, it outputs the refusal template instead of guessing.
