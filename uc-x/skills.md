# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

- name: retrieve_documents
  description: "Loads all three policy files and indexes their contents by document name and section number."
  input: "List of three local filesystem path strings: ../data/policy-documents/policy_hr_leave.txt, ../data/policy-documents/policy_it_acceptable_use.txt, and ../data/policy-documents/policy_finance_reimbursement.txt."
  output: "Structured document index containing document_name, section_number, section_title, original_text, and searchable normalized text for each section."
  error_handling: "Fail with a clear error if any required file is missing, unreadable, empty, not a .txt file, or cannot be parsed into section-numbered content; do not merge sections across documents or infer missing policy text."

- name: answer_question
  description: "Searches the indexed policy documents and returns a single-source cited answer or the exact refusal template."
  input: "Structured document index from retrieve_documents and a user question string from the interactive CLI."
  output: "Plain-text answer containing factual claims from exactly one source document with source document name and section number citations, or the exact refusal template when not covered."
  error_handling: "Refuse with the exact refusal template when the question is not covered, would require combining claims from multiple documents, is ambiguous across documents, or would require unsupported inference; never use hedging phrases such as \"while not explicitly covered\", \"typically\", \"generally understood\", or \"it is common practice\"; preserve all source conditions and cite document name plus section number for every factual claim."
