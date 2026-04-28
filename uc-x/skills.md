- name: retrieve_documents
  description: Loads all three policy files and indexes their content by document name and section number for question answering.
  input: List of three file paths (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
  output: Dictionary mapping document name and section number to content
  error_handling: Raises error if any file is missing; if a section number is malformed, logs warning and skips that section

- name: answer_question
  description: Searches indexed policy documents for an answer to a user question, returning a single-source answer with citation or the refusal template.
  input: User question string, indexed documents dictionary
  output: Answer string with document name and section citation, OR refusal template verbatim
  error_handling: If question spans multiple documents, returns refusal template; if no match found, returns refusal template exactly; never blends sources
