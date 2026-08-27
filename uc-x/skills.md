# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, parses sections by document name and section number, builds searchable index.
    input: Directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: dict with keys = document names (e.g., 'HR', 'IT', 'Finance'), values = dict of {section_number: section_text}.
    error_handling: Rejects if any required file missing. Rejects if section structure cannot be parsed. Returns error message with missing files or parse failure reason.

  - name: answer_question
    description: Searches indexed documents by keyword, returns single-source answer with citation OR exact refusal template — never blends across documents.
    input: question (string), indexed_documents (dict from retrieve_documents), refusal_template (string).
    output: {answer: string, source: string or 'REFUSAL', section: string or null}. Single document source only.
    error_handling: If question found in multiple documents → refuse (ambiguous). If question not found → return refusal_template verbatim. If answer requires info from 2+ sections → refuse. Rejects hedging language; returns only factual citations or refusal.
 