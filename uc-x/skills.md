skills:
  - name: retrieve_documents
    description: Loads multiple policy .txt files, parsing and indexing their content by document name and section number.
    input:
      - name: document_paths
        type: list of strings
        format: A list of file paths to the policy .txt documents (e.g., ["../data/policy_hr_leave.txt", ...]).
    output:
      type: Dict[str, Dict[str, str]]
      format: A nested dictionary where the outer keys are document names (e.g., "policy_hr_leave.txt") and the inner dictionaries map clause numbers (e.g., "2.3") to their full text content.
    error_handling: Catches and logs FileNotFoundError for missing documents, returning an empty dictionary for that document. Returns an empty overall dictionary if no documents can be retrieved or parsed.

  - name: answer_question
    description: Searches indexed policy documents to answer a natural language question, ensuring single-source claims, proper citation, and adherence to refusal conditions.
    input:
      - name: user_question
        type: string
        format: A natural language question from the user (e.g., "Can I carry forward unused annual leave?").
      - name: indexed_documents
        type: Dict[str, Dict[str, str]]
        format: The structured, indexed policy documents as produced by 'retrieve_documents'.
      - name: refusal_template
        type: string
        format: The exact refusal message to use when a question is not covered or violates enforcement rules.
    output:
      type: string
      format: The answer to the question including document and section citation, or the verbatim refusal template.
    error_handling: Returns the refusal_template if the question cannot be answered from a single document, requires blending, or is not covered in any document.

