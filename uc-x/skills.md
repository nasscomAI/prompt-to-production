# skills.md — UC-X Document Q&A System

skills:
  - name: retrieve_documents
    description: Load all 3 policy documents and index them by document name and section number for rapid searching.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dict with structure {document_name: {section_number: section_text}}. Each section indexed as (e.g.) "HR policy section 2.6", "IT policy section 3.1", etc.
    error_handling: If file not found, log error and skip. If file is empty, log warning. Return index with all available sections.

  - name: answer_question
    description: Search indexed documents for answer, returning single-source response with citation or exact refusal template.
    input: Question (string), indexed documents dict from retrieve_documents.
    output: String response - either "[Document] section X.Y: [factual answer]" OR exact refusal template. Never blends sources. Never uses hedging phrases.
    error_handling: If question is ambiguous or touches multiple documents, return refusal template. If no match found in any document, return refusal template exactly as specified. Never guess or invent information.
