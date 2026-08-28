skills:

- name: retrieve_documents
  description: Loads the three target corporate policy text files from the filesystem and indexes their contents hierarchically by document filename and section number.
  input:type: "array"format: >A list of string filesystem paths pointing to the target policy text documents.
  output:type: "object"format: >A structured nested dictionary mapping document names and section keys to their explicit text clauses.
  error_handling: >Aborts application execution if any of the target files are missing, empty, or unreadable; raises an execution error if section boundaries cannot be structurally isolated during indexing.

- name: answer_question
  description: Searches the indexed policy repository to locate single-source answers, appending precise section citations or executing the mandatory verbatim refusal template.input:type: "object"format: >A configuration map containing the user's string query and the indexed structured document dictionary.
  output:type: "string"format: >A clean, single-source response text block displaying full section citations, or the exact predefined verbatim refusal text statement.
  error_handling: Outputs the exact verbatim refusal template if the query content is absent, ambiguous, or triggers multi-document cross-blending parameters; systematically blocks hedging text strings if any data gaps or missing conditions are encountered.
