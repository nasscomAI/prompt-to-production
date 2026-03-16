# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance) and indexes them by document name and section number for precise retrieval.
    input: Paths to the 3 policy .txt files.
    output: A structured index mapping document names and section numbers to their text content.
    error_handling: Return an error if any of the specified policy files are missing or malformed.

  - name: answer_question
    description: Searches the indexed documents and returns a strictly single-source answer with a citation, or explicitly uses the refusal template if the answer is not found.
    input: The user's question as a string context and the indexed policy data.
    output: A single-source answer string with citation (Document Name + Section Number) OR the exact refusal template string.
    error_handling: If the answer requires blending documents or the question cannot be answered cleanly, immediately return the exact refusal template: 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'
