skills:
  - name: retrieve_documents
    description: Loads the three required policy text files and indexes their content strictly by document name and numbered sections.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index containing the parsed text, rigidly grouped by the source document name and its numbered sections.
    error_handling: If any of the required documents are missing or unreadable, halt execution and raise an immediate FileNotFoundError.

  - name: answer_question
    description: Searches the indexed documents to find a matching policy clause, returning a single-source explicit answer with a citation, or the mandated refusal template.
    input: The user's question (string) and the structured index from retrieve_documents.
    output: A direct text answer containing the policy ruling, the cited document name, and the section number; OR the exact verbatim refusal template.
    error_handling: If the answer requires blending rules from multiple distinct documents, or if the question is genuinely not covered explicitly within the text, immediately yield the verbatim refusal template.
