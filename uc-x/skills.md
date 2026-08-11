# skills.md — UC-X Ask My Documents

## Skill: retrieve_documents
- **Input**: List of document file paths (`policy_hr_leave.txt`, `policy_it_acceptable_use.txt`, `policy_finance_reimbursement.txt`).
- **Process**: Read all policy text files, index by filename, section header (e.g. 1, 2, 3), and clause numbers (e.g. 2.6, 3.1, 5.2).
- **Output**: Indexed policy corpus with section numbers and text snippets.

## Skill: answer_question
- **Input**: User question text string.
- **Process**:
  1. Search indexed documents for matching keywords and intent.
  2. Identify if the query is covered by a SINGLE document section.
  3. If relevant content exists in multiple documents, select the single authoritative document for that specific domain (e.g. IT devices -> IT policy; leave -> HR policy; expenses -> Finance policy) to prevent cross-document blending.
  4. If the question is not covered by any document section, output the EXACT refusal template:
     `This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.`
  5. Format answer with exact citation: `[Source: <filename>, Section <X.Y>]`.
- **Output**: Formatted answer string + citation OR refusal template.
