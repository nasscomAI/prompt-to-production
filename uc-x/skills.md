# skills.md — UC-X Policy Q&A Agent

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number for single-source lookup.
    input: document_paths (list of str) — paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: dict mapping (document_name, section_number) → section_text; e.g. ('policy_hr_leave.txt', '5.2') → 'Leave without pay requires...'.
    error_handling: If any file is missing, raise FileNotFoundError naming the missing file — do not proceed with partial documents. If a document has no detectable section structure, raise ValueError stating the document name and that it cannot be indexed.

  - name: answer_question
    description: Searches the indexed documents for a question and returns a single-source answer with citation, or the exact refusal template if the question is not covered.
    input: question (str), index (dict) — output of retrieve_documents.
    output: str — either a direct answer quoting the relevant clause and citing [document_name, section N], or the verbatim refusal template if no single document covers the question.
    error_handling: If the answer would require combining claims from two different documents, do not combine — output the refusal template. If hedging language would be needed to answer, do not answer — output the refusal template. Never return a partial or speculative answer.
