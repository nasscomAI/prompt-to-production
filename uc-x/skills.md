# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and section number.
    input: None
    output: A dictionary or structured object containing the indexed contents of policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    error_handling: Log a critical error and inform the user if any of the three policy files are missing or inaccessible.

  - name: answer_question
    description: Searches the indexed policy documents to find a specific answer and returns it with a citation, or returns the standardized refusal template.
    input: question (string), indexed_docs (structured object)
    output: A string containing the answer plus citation (document name + section), or the verbatim refusal template.
    error_handling: Return the standardized refusal template if the answer is not found, or if answering would require blending information from multiple documents.
