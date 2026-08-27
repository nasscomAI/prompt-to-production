skills:
  - name: retrieve_documents
    description: Loads three policy files and indexes by document and section number.
    input: |
      Paths to: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
    output: |
      Index: {document_name: {section_number: section_text}}, plus raw full text and load status.
    error_handling: |
      - If a file is missing/unreadable: return partial index and a needs_review flag; continue with available files.

  - name: answer_question
    description: Answers from a single document with citation or returns the refusal template.
    input: |
      Question string and the indexed documents from retrieve_documents.
    output: |
      Either: an answer citing "Source: <document> §<section>", or the exact refusal template.
    error_handling: |
      - If multiple documents would need to be combined: return the refusal template.
      - If no section directly covers the question: return the refusal template.
