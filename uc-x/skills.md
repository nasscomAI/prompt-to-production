# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy documents and indexes them by document name and section number for searchable retrieval.
    input: File paths (list of strings) to three policy documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dict with structure {"policy_name": {"section_number": section_text, ...}, ...}. Example: {"policy_hr_leave.txt": {"2.6": "Max 5 days carry-forward...", "5.2": "LWP requires..."}}.
    error_handling: If file not found, raise FileNotFoundError with path. If file contains no numbered sections, raise ValueError. If section parsing fails, raise ValueError with document name and line number.

  - name: answer_question
    description: Searches indexed documents for question answer, returns single-source factual answer with citation OR exact refusal template — never blends documents or uses hedging language.
    input: Dict {\"question\": string, \"indexed_docs\": output_from_retrieve_documents}.
    output: Dict {\"answer\": string, \"source\": \"document_name + section_number\" OR \"REFUSAL\", \"cited\": boolean}. If REFUSAL, answer is exact template.
    error_handling: If answer spans multiple documents, return REFUSAL with template. If hedging needed (while not explicit, typically, etc.), return REFUSAL with template. If question not in documents, return REFUSAL with template. Never return partial/speculative answers.
