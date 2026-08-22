skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: None. Reads hardcoded policy document paths: ../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, ../data/policy-documents/policy_finance_reimbursement.txt.
    output: A list of dictionary objects representing sections/clauses, each containing document_name, section_number, section_heading, and section_text.
    error_handling: Raises FileNotFoundError if any of the three policy files are missing.

  - name: answer_question
    description: Searches the indexed documents for a specific user question, returning a single-source answer + citation or the refusal template.
    input: The user question (string) and the list of indexed document sections.
    output: A string containing the single-source answer text and its citation (document name + section number), or the verbatim refusal template.
    error_handling: Handles empty/whitespace queries by returning the refusal template.
