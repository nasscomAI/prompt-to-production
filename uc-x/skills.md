skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads the three policy text files and indexes their contents by document name and numbered section.

&#x20;   input: Paths to policy\_hr\_leave.txt, policy\_it\_acceptable\_use.txt, and policy\_finance\_reimbursement.txt.

&#x20;   output: Structured document index containing each document filename, section number, and source text.

&#x20;   error\_handling: If a document cannot be read, report the file error and do not invent or reconstruct missing policy content.



&#x20; - name: answer\_question

&#x20;   description: Searches the indexed policy documents and returns a single-source answer with an exact document and section citation or the required refusal template.

&#x20;   input: A user policy question and the structured document index.

&#x20;   output: A factual answer supported by one document and section citation, or the exact refusal template when the question is not covered or would require cross-document blending.

&#x20;   error\_handling: If the question is ambiguous, unsupported, or requires combining claims from multiple documents, use the exact refusal template rather than guessing or blending sources.

