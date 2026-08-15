skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads the three policy documents and indexes their content by document name and section number.

&#x20;   input: Three UTF-8 policy text files.

&#x20;   output: Indexed collection of policy sections grouped by document.

&#x20;   error\_handling: Rejects missing or unreadable documents and never substitutes outside information.



&#x20; - name: answer\_question

&#x20;   description: Finds the relevant policy section and returns a single-source answer with citation or the exact refusal template.

&#x20;   input: User question and indexed policy documents.

&#x20;   output: Answer with document name and section citation, or the exact refusal template.

&#x20;   error\_handling: Refuses when the question is not covered or when answering would require unsupported cross-document inference.

