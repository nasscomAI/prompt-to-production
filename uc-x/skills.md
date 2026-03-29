# Skills for UC-X — Ask My Documents

This file defines the core technical capabilities required for the UC-X policy question-answering system.

## `retrieve_documents`
- **Description**: Loads all policy files and indexes them for efficient retrieval.
- **Functionality**:
    - Reads `policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, and `policy_finance_reimbursement.txt`.
    - Indexes content by document name and section number.
    - Handles file reading errors gracefully.

## `answer_question`
- **Description**: Searches the indexed documents to provide a precise, cited answer or a refusal if the information is missing.
- **Functionality**:
    - Performs search across the indexed policy documents.
    - Ensures single-source answers (no cross-document blending).
    - Returns the answer with a citation (document name + section number).
    - Uses the exact refusal template if no relevant information is found.
    - Strictly avoids hedging or hallucinations.
