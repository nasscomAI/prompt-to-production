\# UC-X Skills



\## retrieve\_documents



\### Purpose

Load and index all three available policy documents.



\### Documents

\- policy\_hr\_leave.txt

\- policy\_it\_acceptable\_use.txt

\- policy\_finance\_reimbursement.txt



\### Behavior

\- Load the policy files from the policy-documents directory.

\- Index content by document name and section number.

\- Preserve the original policy wording.

\- Make individual sections available for retrieval.

\- Do not merge sections from different documents into one answer.



\---



\## answer\_question



\### Purpose

Answer a user's policy question using the indexed policy documents.



\### Behavior

1\. Search the indexed policy sections for the user's question.

2\. Identify the relevant single source document and section.

3\. Return the answer from that source section.

4\. Include the source document name and section number.

5\. Preserve conditions, limits, prohibitions, exceptions, dates, and approval requirements.

6\. Never combine factual claims from different policy documents.

7\. Never use unsupported assumptions or general company practice.

8\. Never use hedging phrases such as:

&#x20;  - "while not explicitly covered"

&#x20;  - "typically"

&#x20;  - "generally understood"

&#x20;  - "it is common practice"



\### Refusal behavior



If the question is not covered by the available policy documents, return this exact text:



This question is not covered in the available policy documents

(policy\_hr\_leave.txt, policy\_it\_acceptable\_use.txt, policy\_finance\_reimbursement.txt).

Please contact \[relevant team] for guidance.



Do not modify, shorten, or expand the refusal template.



\### Cross-document rule



A question must be answered from one source document only.



Information from another document must never be used to create permission, approval, or interpretation that is not explicitly stated in the selected source.



\### Error handling



If a relevant section cannot be confidently identified, refuse using the exact refusal template rather than guessing.

