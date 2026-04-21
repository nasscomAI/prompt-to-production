skills:
  - name: retrieve_documents
    description: Loads the three required policy files and strictly indexes their contents by document name and section number.
    input: File paths to the policy documents (list of strings).
    output: A structured index of the policies organized by document name and section number (dictionary/object).
    error_handling: Raises a fatal error and stops execution if any of the three required policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to answer the user's question, providing a single-source answer with an exact citation or issuing a strict refusal.
    input: The user's question (string) and the structured document index.
    output: A clear answer citing the exact source document name and section number, OR the verbatim refusal template (string).
    error_handling: If the answer requires blending claims from multiple documents, uses hedging phrases, or is simply not found in the text, it immediately aborts the attempt and returns the EXACT refusal template: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
