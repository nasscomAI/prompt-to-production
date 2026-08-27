# UC-X skills

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by document name and section number.
    input: |
      Paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    output: |
      A structured index containing document names, section numbers, and clause text for each section.
    error_handling: |
      - If a file cannot be read, raise a clear error.
      - If section numbers cannot be parsed, report the parsing failure and stop.

  - name: answer_question
    description: Search the indexed documents and return a single-source answer with citation or an exact refusal.
    input: |
      A question string and the structured document index from `retrieve_documents`.
    output: |
      A text answer that either cites a single source section or returns the exact refusal template.
    error_handling: |
      - If the answer requires combining information from multiple documents, return the exact refusal template.
      - If the question is not covered by any document, return the exact refusal template.
      - Do not use hedging language or partial answers.

notes: |
  - The answer must cite the source document name and section number for every factual claim.
  - The refusal template must be used exactly when the question is not contained in the documents.
  - Avoid blending information from HR, IT, and Finance into a single response unless one document alone fully covers the answer.
