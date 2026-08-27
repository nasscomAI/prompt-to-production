# skills.md

skills:
  - name: retrieve_documents
    description: Load 3 policy documents, extract sections by ID (e.g., 2.3, 3.1), and index by document name and section number.
    input: "File paths to 3 policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)"
    output: "Indexed dictionary: {document_name -> {section_id -> section_text}}; all sections are fully parsed and searchable; document name, section ID, and full text preserved"
    error_handling: "If file not found, raise FileNotFoundError with filepath. If section format invalid, skip malformed sections and report count of valid sections loaded"

  - name: answer_question
    description: Search indexed documents for single-source answer to policy question; return answer + citation or refusal template.
    input: "Question (string), indexed documents (dict), refusal template (string)"
    output: "Tuple (answer_text, source_document_name, section_id); if answer found in exactly one document, return answer + citation; if not found or ambiguous, return REFUSAL_TEMPLATE with None for source and section"
    error_handling: "If question could be answered by 2+ documents, return REFUSAL_TEMPLATE (refuse to blend). If question not in any document, return REFUSAL_TEMPLATE exactly, no paraphrasing. Never use hedging phrases in any output"
