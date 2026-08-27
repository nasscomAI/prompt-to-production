# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt (list of strings).
    output: An indexed dictionary mapping each (document_name, section_number) pair to the corresponding section text.
    error_handling: If any file is missing or unreadable, raise an error naming the missing file. Do not proceed with partial data.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question, returning the answer with citation or the refusal template.
    input: A natural-language question string and the indexed document dictionary from retrieve_documents.
    output: A single-source answer citing the document name and section number, OR the exact refusal template if the question is not covered.
    error_handling: If the question matches content in multiple documents, answer from a single document only — do not blend. If genuine ambiguity exists across documents, return the refusal template.
