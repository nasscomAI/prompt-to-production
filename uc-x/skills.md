skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy documents by document name and section number.
    input:
      type: file_paths
      format: list of paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt
    output:
      type: indexed_document_collection
      format: documents keyed by document name, with content organized by section number
    error_handling:
      - Reject missing, unreadable, or unexpected files and report the specific file error.
      - Do not create inferred content or silently continue with an incomplete document set.

  - name: answer_question
    description: Searches the indexed policy documents and returns a single-source answer with citation or the exact refusal template.
    input:
      type: question
      format: plain-text policy question
    output:
      type: answer
      format: single-source answer citing document name and section number for every factual claim, or the exact refusal template
    error_handling:
      - For invalid or empty questions, request a valid policy question without guessing.
      - For ambiguous questions that would require combining documents, refuse using the exact refusal template.
      - Never combine claims from different documents or drop source conditions, limits, prohibitions, approvals, or dates.
      - Never use hedging phrases such as "while not explicitly covered", "typically", "generally understood", or "it is common practice".
      - For questions not covered by the documents, return exactly:
          This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
          Please contact [relevant team] for guidance.
      - Reject answers without a document name and section number citation for each factual claim.
