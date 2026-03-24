skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and indexes their contents by document name and section number, making them searchable for the answer_question skill.
    input: A list of three file paths — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt — provided as strings.
    output: An indexed document store where each entry is keyed by document name and section number, containing the full text of that section.
    error_handling: If a file is not found at the given path, log the missing filename and skip it. If all three files fail to load, halt and return an error message stating that no policy documents are available.
 
  - name: answer_question
    description: Searches the indexed policy documents for an answer to a user's question, returning a single-source answer with a document and section citation, or the standard refusal template if no answer is found.
    input: A plain-text question string from the user.
    output: A text response containing either (a) the answer drawn from one document with citation in format [Document name, Section X.X], or (b) the exact refusal template if the question is not covered in any document.
    error_handling: If the question matches content in more than one document, do not blend — return only the most directly relevant single-source answer. If the question is ambiguous or cannot be reliably matched to any section, return the refusal template rather than guessing.
 