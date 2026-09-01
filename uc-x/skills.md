skill: retrieve_documents
description: >
  Loads all three policy files from ../data/policy-documents/ and indexes them by document name and section number.
parameters:
  - name: policy_dir
    type: string
    default: "../data/policy-documents/"
    description: Directory containing the three policy text files
returns:
  index: object with keys "policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"
  description: Each value is an object mapping section numbers (e.g., "2.6") to section text content.
behavior: |
  1. Read all three .txt files from the policy directory
  2. Parse each file into sections by detecting numbered headings (e.g., "2.6 Carry Forward of Annual Leave")
  3. Build an index: {doc_name: {section_num: section_text}}
  4. Return the complete index for use by answer_question

---

skill: answer_question
description: >
  Searches the indexed documents for a question, returns a single-source answer with citation OR the exact refusal template.
parameters:
  - name: question
    type: string
    description: User's question
  - name: index
    type: object
    description: Output from retrieve_documents
returns:
  answer: string — either a factual answer citing exactly one document.section, or the refusal template
behavior: |
  1. For each document in the index, search sections for content relevant to the question
  2. If exactly ONE document contains a relevant section:
     - Return the verbatim answer from that section
     - Append citation: " (source: policy_hr_leave.txt section 2.6)"
  3. If MULTIPLE documents contain relevant sections:
     - DO NOT blend — return refusal template
  4. If NO document contains relevant content:
     - Return refusal template exactly
  5. Never include hedging phrases
  6. Refusal template (verbatim):
     "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."