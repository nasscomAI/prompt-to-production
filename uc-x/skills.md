# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
- name: retrieve_documents
  description: Loads the HR, IT, and Finance policy files and creates a searchable index organized by document filename and section numbers.
  input: None (operates on pre-defined local paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt).
  output: A structured JSON object containing indexed text blocks mapped to their source filenames and respective section identifiers.
  error_handling: If any of the three mandatory policy files are missing or unreadable, the skill returns a retrieval error; if section boundaries are ambiguous, it defaults to a clean partition to prevent condition dropping.
- name: answer_question
  description: Queries the indexed policy documents to provide a factual, single-source answer with mandatory citations or the specific refusal template.
  input: User inquiry provided as a plain text string.
  output: A formatted text response containing a factual claim and its citation (Filename + Section Number) or the verbatim refusal template.
  error_handling: If a question results in cross-document blending, requires hedging, or cannot be answered using a single document, the skill returns the exact refusal template to prevent hallucination.
