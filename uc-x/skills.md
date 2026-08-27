# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes content by document name and section number
    input: "list of file paths: [policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt]"
    output: "dict with keys: documents (dict of doc_name -> {sections: dict, content: str}), index (searchable index)"
    error_handling: "If file not found, raise FileNotFoundError. If file is empty, return empty content."

  - name: answer_question
    description: Searches indexed documents for question, returns single-source answer with citation OR refusal template
    input: "question (str), documents_index (dict), refusal_template (str)"
    output: "dict with keys: answer (str), source_doc (str or None), source_section (str or None), is_refusal (bool)"
    error_handling: "If no relevant content found, return refusal template. Never blend multiple documents."
