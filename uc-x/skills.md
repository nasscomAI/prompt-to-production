# skills.md — UC-X Ask My Documents Skills

skills:
  - name: retrieve_documents
    description: Load and index all three policy documents by document name and numbered section.
    input: "Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
    output: "Structured index containing document_name, section_id, and section_text for retrieval and citation."
    error_handling: "If any file is missing or unreadable, return a hard retrieval error naming the file. If section numbering is malformed, return partial index with parse warnings and do not invent section IDs."

  - name: answer_question
    description: Answer user questions using one document section at a time, with citation, or return exact refusal template.
    input: "User question string + structured index from retrieve_documents."
    output: "Either a single-source policy answer with document+section citation for each claim, or exact refusal template text when not covered/ambiguous."
    error_handling: "If evidence is missing, ambiguous, or requires combining claims across documents, output the refusal template exactly: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
