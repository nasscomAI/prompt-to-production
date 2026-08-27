
# skills.md

## Overview
This file defines the core capabilities ("skills") available to the UC-X system.
Each skill is deliberately narrow to prevent cross-document blending, hedged
hallucinations, and condition dropping. [1](https://iriworldwide-my.sharepoint.com/personal/sudipt_nigam_circana_com/Documents/Microsoft%20Copilot%20Chat%20Files/README.md)

---

## Skill: retrieve_documents

### Purpose
Load and index the approved policy documents so they can be queried reliably
by document name and section number.

### Documents Loaded
- policy_hr_leave.txt
- policy_it_acceptable_use.txt
- policy_finance_reimbursement.txt [1](https://iriworldwide-my.sharepoint.com/personal/sudipt_nigam_circana_com/Documents/Microsoft%20Copilot%20Chat%20Files/README.md)

### Behaviour Rules
- Index documents **separately**, never as a merged corpus.
- Preserve original section numbers and headings.
- Do not infer relationships between documents.

### Output
A structured index:
- Document name
- Section number
- Exact section text

---

## Skill: answer_question

### Purpose
Answer user queries using **only one policy document** as the source,
or refuse when the answer is not explicitly present.

### Process
1. Search the indexed documents for a **single-source** match.
2. If exactly one document and section fully answers the question:
   - Return the answer verbatim or paraphrased conservatively.
   - Cite the document name and section number.
3. If the answer:
   - Requires combining multiple documents, OR
   - Is not clearly stated in any document
   → respond with the refusal template **exactly** as written.

### Mandatory Refusal Template
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance. [1](https://iriworldwide-my.sharepoint.com/personal/sudipt_nigam_circana_com/Documents/Microsoft%20Copilot%20Chat%20Files/README.md)

### Forbidden Behaviours
- Cross-document blending
- Hedging language (e.g., "typically", "while not explicitly covered")
- Providing policy “interpretations” or assumptions

---

## Design Principle
Every successful answer must be:
- Single-source
- Explicitly stated
- Fully cited

When in doubt, **refuse**. [1](https://iriworldwide-my.sharepoint.com/personal/sudipt_nigam_circana_com/Documents/Microsoft%20Copilot%20Chat%20Files/README.md)
