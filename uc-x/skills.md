skills:

&#x20; - name: retrieve\_documents

&#x20;   description: >

&#x20;     Loads all three available policy documents and indexes their content by

&#x20;     document name and section number so that answers can be traced to the

&#x20;     exact source.

&#x20;   input:

&#x20;     documents:

&#x20;       - policy\_hr\_leave.txt

&#x20;       - policy\_it\_acceptable\_use.txt

&#x20;       - policy\_finance\_reimbursement.txt

&#x20;   output: >

&#x20;     Structured document index containing document name, section number,

&#x20;     and the corresponding source text.

&#x20;   error\_handling: >

&#x20;     If any required document is missing, empty, or unparseable, report the

&#x20;     specific document problem and do not invent or substitute content from

&#x20;     external knowledge.



&#x20; - name: answer\_question

&#x20;   description: >

&#x20;     Answers a policy question using only the indexed policy documents.

&#x20;     Each factual claim must come from exactly one source document and must

&#x20;     include the source document name and section number.

&#x20;   input:

&#x20;     question: str

&#x20;   output: >

&#x20;     A concise answer grounded in a single source document with document name

&#x20;     and section number citation, or the exact refusal template when the

&#x20;     question is not covered or cannot be answered without combining documents.

&#x20;   error\_handling: >

&#x20;     Never blend claims from multiple documents, never infer missing policy

&#x20;     information, and never use hedging language. If the question is not

&#x20;     explicitly covered, return exactly:

&#x20;     This question is not covered in the available policy documents

&#x20;     (policy\_hr\_leave.txt, policy\_it\_acceptable\_use.txt, policy\_finance\_reimbursement.txt).

&#x20;     Please contact \[relevant team] for guidance.

