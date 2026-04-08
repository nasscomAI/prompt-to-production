# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Ingests all policy text files and securely indexes them by document name and section number to prevent hallucination and support strict citation mapping.
    input: File paths to `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    output: A structured vector or exact-match index strictly mapping text segments to their source document and clause numbers.
    error_handling: Halts and alerts if a document is unreadable or fails to have distinct section numbering.

  - name: answer_question
    description: Searches the indexed documents to return a definitive, single-source answer with formal citations, or strictly deploys the refusal template if the answer is absent.
    input: A natural language user question paired with the structured index from `retrieve_documents`.
    output: A precise answer exclusively containing text from one source document with exact section citations, OR the exact verbatim refusal template.
    error_handling: Automatically falls back to the exact refusal template if standard retrieval fails, if cross-document blending is detected, or if confidence thresholds fall.
