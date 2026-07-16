skills:
  - name: retrieve_documents
    description: >
      Loads the three policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt) and indexes their contents by document name and section/clause number.
    input: >
      None.
    output: >
      dict — a structured key-value index mapping (doc_name, section_number) to the text content of that clause.
    error_handling: >
      Raises FileNotFoundError if any of the three policy files cannot be found.

  - name: answer_question
    description: >
      Analyzes the user's question, performs a single-source document search,
      and returns either a precise answer with citations or the exact refusal template.
    input: >
      question (str) — the user's question; index (dict) — the document index from retrieve_documents.
    output: >
      str — the final answer with section/document citation, or the exact refusal template.
    error_handling: >
      Raises ValueError if the input question is empty.
      If the question matches a known ambiguous query or is not covered in the documents,
      returns the verbatim refusal template.
