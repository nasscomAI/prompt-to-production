# \# skills.md — UC-X Ask My Documents

# 

# skills:

# &#x20; - name: retrieve\_documents

# &#x20;   description: >

# &#x20;     Loads the three supplied policy documents and indexes their content

# &#x20;     by document name and section number.

# 

# &#x20;   input: >

# &#x20;     policy\_hr\_leave.txt, policy\_it\_acceptable\_use.txt,

# &#x20;     policy\_finance\_reimbursement.txt

# 

# &#x20;   output: >

# &#x20;     An indexed collection of policy sections, preserving the source

# &#x20;     document name and section number.

# 

# &#x20;   error\_handling: >

# &#x20;     If a document cannot be loaded, stop and report the missing document.

# &#x20;     Do not use outside information.

# 

# &#x20; - name: answer\_question

# &#x20;   description: >

# &#x20;     Searches the indexed policy sections and answers a question using

# &#x20;     only one source document. Every factual answer must cite the source

# &#x20;     document name and section number.

# 

# &#x20;   input: >

# &#x20;     A user policy question and the indexed policy documents.

# 

# &#x20;   output: >

# &#x20;     A factual single-source answer with document name and section

# &#x20;     citation, or the exact refusal template when the question is not

# &#x20;     covered or would require combining documents.

# 

# &#x20;   error\_handling: >

# &#x20;     Never combine claims from different documents. Never guess or infer

# &#x20;     missing policy conditions. If the question is not covered, return

# &#x20;     the exact refusal template without variation.

