# skills.md

skills:
  - name: retrieve_documents
    description: Load the three policy documents and index them by document name and section number so the agent can retrieve relevant policy text for a question.
    input: A list of document paths or a repository-relative folder containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index of policy sections keyed by document name and section number, including the section text needed to answer questions.
    error_handling: If a document is missing or unreadable, report the issue and do not answer from incomplete context.

  - name: answer_question
    description: Search the indexed policy documents for the best matching single-source answer and return a grounded response with citation or the required refusal template.
    input: A user question as a string and the indexed policy document store.
    output: A response string containing either a single-source answer with the source document name and section number, or the exact refusal template when the question is not covered.
    error_handling: If the question is ambiguous, partially covered, or spans multiple documents, refuse or answer from the most directly relevant single source only; never blend sources.
