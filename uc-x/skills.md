skills:
  - name: retrieve_documents
    description: Loads all three policy documents, parses section numbering, and returns indexed document structure ready for answering.
    input: "None (runs at startup); requires file paths: ../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, ../data/policy-documents/policy_finance_reimbursement.txt"
    output: "Indexed document object: { 'HR': { '2.6': 'exact text', '5.2': 'exact text', ... }, 'IT': { '3.1': 'exact text', '2.3': 'exact text', ... }, 'Finance': { '3.1': 'exact text', '2.6': 'exact text', ... } }"
    error_handling: "If any file is missing, unreadable, or cannot be parsed for section numbers, refuse to start CLI and return: 'Error: One or more policy documents are missing or unreadable. The system requires all three policy files to operate.'"

  - name: answer_question
    description: Searches indexed documents for single-source answers, detects cross-document attempts, bans hedging language, and returns cited answer or refusal template.
    input: "User question (string); indexed document structure from retrieve_documents()"
    output: "Single answer with citation in format 'Policy: [document] section [number]: [exact statement from document]' OR refusal template, never blended"
    error_handling: "If question matches content in multiple documents (cross-document risk), refuse with: 'This question may require information from multiple policy documents. Please ask a more specific question focusing on one area (HR leave, IT policy, or Finance reimbursement).' If question not in any document, return refusal template verbatim. If answer would require hedging phrases, refuse instead. If question is answered but no section number can be found, refuse to answer without citation."
