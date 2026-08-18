# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their sections by document name and clause number so the assistant can answer from a single source.
    input: The paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A dictionary of document names mapped to section headings and their text content.
    error_handling: If a document is missing or unreadable, returns a clear error message instead of answering from incomplete data.

  - name: answer_question
    description: Searches the indexed policy sections for the best single-source answer, or returns the exact refusal template when the question is out of scope.
    input: A user question as a string and the loaded document index.
    output: A response string that is either a factually supported answer with a citation or the exact refusal template.
    error_handling: If multiple documents appear relevant, refuses rather than blending them into a single answer.
