# skills.md — UC-X Policy Q&A

skills:
  - name: retrieve_documents
    description: Loads all three policy documents, indexes content by document name and section number.
    input: List of three file paths: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: Dictionary keyed by document name, containing dict of section_number -> section_text.
    error_handling: >
      If any file not found: raise FileNotFoundError listing missing file.
      If file is empty: raise ValueError with document name.

  - name: answer_question
    description: Searches indexed documents for question relevance, returns single-source answer with citation OR refusal template.
    input: question (string), indexed_documents (dict from retrieve_documents)
    output: Dictionary with keys: answer (string), source (string: document name or "REFUSAL"), section (string or null), is_refusal (bool)
    error_handling: >
      If question not covered in any document: return refusal template exactly.
      If question requires blending two documents: either answer from one document only OR return refusal.
      Never return "I'm not sure", "it may be", "typically", etc.
