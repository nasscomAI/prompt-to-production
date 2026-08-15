# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three policy documents and indexes them by document name and section number.
    input: Paths to the three policy files (../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, ../data/policy-documents/policy_finance_reimbursement.txt).
    output: Indexed documents keyed by document name and section number, available for lookup during answering.
    error_handling: If a file is missing or unreadable, fail loudly — do not answer from general knowledge or partial content.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation, or the refusal template verbatim.
    input: A user question (string) plus the document index built by retrieve_documents.
    output: A single-document answer citing document name + section number, or the verbatim refusal template when the question is not covered.
    error_handling: If the question matches claims in two or more documents, or no single document covers it, return the refusal template exactly — never blend documents, never hedge, never guess.
