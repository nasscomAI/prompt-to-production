# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

- name: retrieve_documents
  description: Loads all three policy files and indexes their content by document name and section number.
  input: File paths (list of strings) to the three policy text files — policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
  output: An indexed structure mapping each document name to its sections, where each section is addressable by section number and contains its text content.
  error_handling: >
  If any of the three files is missing or unreadable, refuses to proceed and
  reports which file could not be loaded rather than answering from a partial
  index. If a document's section numbering cannot be parsed, flags the parsing
  issue rather than silently indexing it as unstructured text, since section
  citation is required for every downstream answer.

- name: answer_question
  description: Searches the indexed documents for a question and returns either a single-source cited answer or the exact refusal template.
  input: A user question (string) and the indexed document structure from retrieve_documents.
  output: >
  Either (a) an answer string containing the factual claim plus its source
  document name and section number citation, drawn from exactly one
  document, or (b) the refusal template returned verbatim with no
  modification.
  error_handling: >
  If the question's answer would require combining content from two or more
  documents, does not synthesize a blended answer — instead returns a
  single-source answer limited to the most directly applicable document's
  section, or returns the refusal template if no single document fully
  answers it. Never uses hedging language in place of a citation or the
  refusal template. If no matching content is found in any document,
  returns the refusal template exactly as specified, without paraphrasing
  or adding caveats.
