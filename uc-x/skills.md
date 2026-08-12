# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number, ready for question answering.
    input: List of paths (strings) — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: dict keyed by document name — each value has metadata (document reference, version, effective date) and sections: list of {section_number, text} parsed from numbered clauses (X.Y)
    error_handling: Fails loudly with a clear message if any path is missing or a file cannot be parsed. Lines that cannot be matched to a section are collected in an unparsed list and surfaced — never silently dropped.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source, cited answer to a question — or the exact refusal template when the question is not covered.
    input: question (string), documents (dict from retrieve_documents)
    output: Answer string in the format "Answer: <claim>. Source: policy_<name>.txt, section X.Y." — one document only, all conditions preserved. If not covered or a cross-document blend would be required, the exact refusal template verbatim: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
    error_handling: Refuses with the exact template whenever the question matches no clause, or when an answer would require combining two documents. Never produces hedging phrases ("while not explicitly covered", "typically", "generally understood", "it is common practice") and never emits an uncited claim.
