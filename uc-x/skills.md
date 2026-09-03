skills:

&#x20; - name: retrieve\_documents

&#x20;   description: >

&#x20;     Loads the three approved policy documents and indexes their content by

&#x20;     document filename and section number without combining content across

&#x20;     documents.

&#x20;   input: >

&#x20;     No external input is required. The skill reads exactly these UTF-8 text

&#x20;     files from ../data/policy-documents:

&#x20;     policy\_hr\_leave.txt,

&#x20;     policy\_it\_acceptable\_use.txt,

&#x20;     policy\_finance\_reimbursement.txt.

&#x20;   output: >

&#x20;     A collection of policy sections where every entry contains the source

&#x20;     filename, section number, and exact section text. Document boundaries and

&#x20;     section identifiers are preserved.

&#x20;   error\_handling: >

&#x20;     If any required policy document is missing, unreadable, or cannot be

&#x20;     parsed into identifiable sections, stop and report the specific problem.

&#x20;     Do not substitute external information or continue with incomplete

&#x20;     policy sources.



&#x20; - name: answer\_question

&#x20;   description: >

&#x20;     Answers a policy question using only one authoritative policy document

&#x20;     and section, or returns the exact refusal template when the documents

&#x20;     do not directly support an answer.

&#x20;   input: >

&#x20;     A question string and the indexed sections returned by

&#x20;     retrieve\_documents. The question must be evaluated against the supplied

&#x20;     policy text only.

&#x20;   output: >

&#x20;     A concise answer supported by a single policy document with the exact

&#x20;     source filename and section number for every factual claim, or the exact

&#x20;     required refusal template when the question is not directly covered or

&#x20;     requires combining documents.

&#x20;   error\_handling: >

&#x20;     Never blend claims from multiple documents. Never infer missing policy

&#x20;     details or use general knowledge. Never use hedging phrases such as

&#x20;     'while not explicitly covered', 'typically', 'generally understood', or

&#x20;     'it is common practice'. If the question is not directly supported by a

&#x20;     single document and section, return exactly:

&#x20;     This question is not covered in the available policy documents

&#x20;     (policy\_hr\_leave.txt, policy\_it\_acceptable\_use.txt, policy\_finance\_reimbursement.txt).

&#x20;     Please contact \[relevant team] for guidance.
