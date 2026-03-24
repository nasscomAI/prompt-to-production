skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: File paths (string list) — ../data/policy-documents/policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt
    output: Indexed document store (dict) mapping document name → section number → section text.
    error_handling: If a file is missing or unreadable, raise an error and halt — do not proceed with partial document sets.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question and returns it with a citation, or returns the exact refusal template if no answer is found.
    input: User question (string) + indexed document store produced by retrieve_documents.
    output: Single-source answer string with citation (document name + section number), OR the verbatim refusal template if the question is not covered in any document.
    error_handling: If the question matches content in more than one document, return the refusal template rather than blending across documents.
