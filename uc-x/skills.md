# skills.md
# Policy Document Q&A Skills

skills:
  - name: retrieve_documents
    description: Loads policy files, indexes content by document name and section number, returns searchable document store.
    input: List of policy file paths (strings).
    output: Dictionary {document_name: [sections], where each section = {section_num, section_title, full_text}}.
    error_handling: Raises error if file not found. Skips malformed sections but reports count of valid sections loaded. Does not continue if any file missing.

  - name: identify_relevant_policy
    description: Scans question against indexed documents, identifies which policy (HR/IT/Finance) is most relevant.
    input: User question (string); indexed document store from retrieve_documents.
    output: List of relevant document names and section numbers (e.g., [('policy_hr_leave.txt', 2.6), ('policy_finance_reimbursement.txt', 2.6)]) or empty list if no match.
    error_handling: Returns empty list if question has no matches. Flags ambiguous questions (matched in 2+ documents) for manual review. Does not guess.

  - name: extract_answer
    description: For a matched section, extracts verbatim conditions, limits, dates, and exceptions from policy text; refuses blending across documents.
    input: Document name; section number(s); policy text; user question.
    output: Citation (document + section); verbatim extract with all conditions, limits, and exceptions; or refusal template if no single-source match.
    error_handling: If question matches both HR and IT, refuses to blend and returns refusal template (unless one policy supersedes). Always shows exact section numbers and conditions. Never summarizes or paraphrases.

