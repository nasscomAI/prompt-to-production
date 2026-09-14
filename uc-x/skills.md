# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: The 3 fixed file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A list of sections, each {doc_name, section_number, text}, covering every numbered section in all 3 files.
    error_handling: A missing file is skipped with a printed warning — the other documents still get indexed and questions still work with reduced coverage.

  - name: answer_question
    description: Resolves a question to a single cited section, or the refusal template, per agents.md.
    input: A question string, the indexed sections list.
    output: Either "[doc_name section_number] <section text>" for a single confident single-document match, or the exact refusal template string.
    anchor_rule: Checked first — a small table of known ambiguous phrasings (e.g. "personal phone", "without pay") maps straight to the one correct section, because plain keyword overlap alone picks the wrong section or ties across documents for these.
    scope_rule: When no anchor matches, falls back to per-document keyword-overlap scoring. If the top two documents score comparably, the question is treated as cross-document-ambiguous and refused rather than blended.
    zero_match_rule: If no section scores above the relevance threshold, return the refusal template unchanged.
    error_handling: Never returns a hedged sentence and never returns text spliced from two sections in two different documents.
