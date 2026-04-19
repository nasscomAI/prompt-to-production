skills:
  - name: retrieve_documents
    description: Loads the three required policy files and strictly indexes the available text by document name and section number.
    input: List of three file paths to the HR, IT, and Finance policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A searchable index mapping document names and section numbers to the relevant policy text.
    error_handling: Refuses to load files outside of the three authorized policy documents or fails gracefully if any file is missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to return a single-source factual answer with exact citation, or triggers the exact refusal template.
    input: The user's question as a string and the searchable document index.
    output: A factual string answer containing the exact source document name and section number, or the mandatory refusal template string.
    error_handling: Returns the exact refusal template if the question is ambiguous, not covered, or would require blending assumptions or claims across multiple policy documents.
