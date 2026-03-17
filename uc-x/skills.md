# skills.md

skills:
  - name: retrieve_documents
    description: Load all three policy documents and index them by document name and section number for rapid lookup.
    input: "Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output: "Indexed dictionary: {document_name: {section_number: content_text}}. Ready for search queries."
    error_handling: "If file not found, raise FileNotFoundError. If file cannot be parsed, return raw content with error flag."

  - name: answer_question
    description: Search indexed documents for a single question, return single-source answer with citation OR refusal template.
    input: "User question (string), indexed documents (from retrieve_documents)"
    output: "Answer: 'Policy: [document_name], Section [number]: [quote/summary]' OR Refusal template (exact wording required)"
    error_handling: "If question matches multiple documents equally, refuse (ambiguous). If no document covers it, use refusal template. Never blend answers."
