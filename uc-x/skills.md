- name: retrieve_documents
  description: Loads the mandatory HR, IT, and Finance policy files and indexes their content specifically by document name and section number.
  input: List of paths to policy documents (strings).
  output: Indexed repository of policy sections mapped to their respective document names and section identifiers.
  error_handling: Aborts if any required file is missing; ensures every loaded section is uniquely identifiable to prevent cross-document confusion.

- name: answer_question
  description: Searches the indexed policies for a single-document match to provide a direct answer with mandatory citations or the standard refusal template.
  input: User query (string) and the indexed policy repository.
  output: Verified answer string containing a single-source citation (Document + Section) or the verbatim refusal template.
  error_handling: Strictly refuses to combine information from multiple documents; defaults to the specific refusal template when matching content is absent or creates ambiguity; removes all hedging language.
