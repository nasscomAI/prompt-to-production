# skills.md — UC-X Document Q&A Skills

skills:
  - name: retrieve_documents
    description: Load and index 3 policy files by document name and section number for searchable retrieval.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dictionary indexed as {doc_name: {section_num: section_text}}. Raises error if any file missing or unreadable.
    error_handling: If file missing, raise error naming the file. If section parsing fails, log warning and include raw section. Continue if 2/3 files present.

  - name: answer_question
    description: Search indexed documents for answer to user question, return single-source answer with citation or refusal template.
    input: User question (string), indexed_documents dict, refusal_template (string).
    output: String containing either (a) Answer from single document with citation [DOCUMENT_NAME, section X.Y], or (b) Refusal template verbatim.
    error_handling: If question matches multiple documents, search each separately and provide both answers OR refuse if ambiguous. If no match, return refusal template.
