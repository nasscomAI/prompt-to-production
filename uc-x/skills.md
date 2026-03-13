skills:
  - name: retrieve_documents
    description: Loads all three policy documents and extracts numbered sections.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: Dictionary indexing sections by document name and containing the numbered clause text.
    error_handling: Return empty dictionary and log error if a document cannot be read.

  - name: answer_question
    description: Finds the most relevant section for a question and returns a single-source answer with citation or the refusal template.
    input: User question text and the document index from retrieve_documents.
    output: A single string with the exact clause text and a citation formatted as "Source: <document_name> section <section_number>", or the refusal template if not found.
    error_handling: If the question cannot be accurately answered or matched to a policy section, return exactly the refusal template.