skills:
  - name: retrieve_documents
    description: Loads and parses the three official policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt), indexing content by document name, section number, and clause text.
    input: policy_dir (str path to policy-documents directory)
    output: dict mapping doc_name -> list of Section objects containing title, section_num, and text
    error_handling: Raises FileNotFoundError if any of the mandatory policy files are missing; logs warnings for unrecognized lines.

  - name: answer_question
    description: Analyzes a user policy inquiry, determines the single most relevant authoritative policy section, extracts the answer without cross-document blending, and outputs the result with full section citations or the mandatory verbatim refusal template.
    input: question (str), indexed_docs (dict)
    output: dict containing keys (status: 'ANSWERED' | 'REFUSED', answer: str, source_doc: str | None, section: str | None)
    error_handling: If the question is ungrounded, ambiguous, or asks for unstated company opinions, returns the exact verbatim refusal template without guessing or using hedging phrases.
