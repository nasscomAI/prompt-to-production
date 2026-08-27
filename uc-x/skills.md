# skills.md — UC-X Document QA Skills

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt) and indexes them by document name, section number, and title.
    input: Directory path string pointing to policy documents folder.
    output: Dictionary mapping document names and section IDs to section text content.
    error_handling: Handles missing policy files by raising FileNotFoundError or returning error status.

  - name: answer_question
    description: Evaluates a user question against indexed documents, extracts single-source factual answer with document name and section citation, or returns exact refusal template if question is out-of-scope.
    input: Question string and indexed documents structure.
    output: String response containing cited answer or exact refusal template.
    error_handling: Automatically returns refusal template if match is ambiguous or missing.
