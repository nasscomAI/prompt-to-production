# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: doc_dir — path to the directory holding policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: A dict { "<filename>": {"title": str, "clauses": {"<section>": "<verbatim text>"}} } for each document. Wrapped continuation lines are joined into their clause so section text is complete.
    error_handling: Divider and blank lines are skipped; section-heading lines are not mistaken for clauses. A clause's continuation lines are appended verbatim rather than dropped, so no condition is lost from a cited section.

  - name: answer_question
    description: Answer a question from a single document with a section citation, or return the refusal template verbatim when not covered.
    input: question (free-text string) and index (the dict from retrieve_documents).
    output: A dict {type: "answer"|"refusal", doc, title, sections, text, question}. An answer quotes the matched section(s) from ONE document and cites document name + section. A refusal carries the exact template text.
    error_handling: Rules are matched in order and the first match wins, so an answer is always single-source — never a blend of two documents. The personal-phone question matches the IT-only rule, never HR. If no rule matches, it returns the refusal template verbatim with no hedging.
