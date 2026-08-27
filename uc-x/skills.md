skills:
  - name: retrieve_documents
    description: Load all three policy files and index by document name and section number for single-source lookups.
    input: Paths to (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: Dictionary {doc_name: {section_num: section_text, ...}, ...} allowing retrieval by document + section, plus flattened keyword index for search
    error_handling: If any file missing, raise FileNotFoundError naming the file. If file unreadable, raise IOError. Return empty dict entry for document rather than crashing.

  - name: answer_question
    description: Search indexed documents for question, return single-source answer with citation OR exact refusal template if not found.
    input: (question string, indexed_documents dict from retrieve_documents, refusal_template string)
    output: Text response containing: (1) Answer from ONE document with section citation, OR (2) EXACT refusal template if question not covered
    error_handling: If question matches content in multiple documents, return answer from first match with clear citation. Never blend documents. If question is ambiguous or requires blend, use refusal template. If exact section match not found, search for partial keyword matches but ONLY if confidence is high — otherwise refusal. All output must be either citation or refusal template — no hedging.

