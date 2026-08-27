skills:
  - name: retrieve_documents
    description: Loads all policy text files (HR, IT, Finance) and parses them into searchable, indexed sections mapped to document references.
    input: List of document file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: Indexed dictionary mapping document reference codes and section numbers to raw clause text.
    error_handling: Handles missing policy files by reporting unreadable files while continuing to index available policy documents.

  - name: answer_question
    description: Evaluates a user question against indexed policy sections, generating a single-source cited response or returning the exact refusal template.
    input: User question string and indexed documents from retrieve_documents.
    output: String containing the answer with single-source policy citation or the exact refusal template.
    error_handling: If the question requires cross-document blending, contains unstated assumptions, or has no direct match, returns the exact refusal template.
