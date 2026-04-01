# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number for efficient retrieval.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A searchable index or structured representation of the documents grouped by section.
    error_handling: Fail explicitly if any of the three core policy files are missing or unreadable.

  - name: answer_question
    description: Searches the document index to find the most relevant single-source answer and returns it with a citation, or returns the refusal template if no match is found.
    input: User's question (string).
    output: A string containing either (a) the answer and section citation or (b) the verbatim refusal template.
    error_handling: Must return the refusal template if the answer requires blending information from multiple documents or if no document contains the answer.
