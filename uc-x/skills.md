# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Reads all policy text files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes sections by document name and section number.
    input: List of document file paths.
    output: Structured index dictionary mapping (doc_name, section_number) to section title and full text.
    error_handling: Handles missing policy files by raising FileNotFoundError; ignores unreadable encoding gracefully.

  - name: answer_question
    description: Evaluates user query against retrieved policy sections, enforces single-source governing attribution, attaches exact document and section citations, and returns the exact refusal template if context is missing or ambiguous.
    input: User question string (str) and structured document index.
    output: Answer string containing factual response + citation OR verbatim refusal template.
    error_handling: Rejects hedging phrases; refuses cross-document blending by selecting single governing policy section.
