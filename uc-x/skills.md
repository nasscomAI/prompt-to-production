\# skills.md — UC-X



skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads all three policy files and indexes their numbered sections by document name and section number.

&#x20;   input: Three UTF-8 policy text files.

&#x20;   output: Structured document and section index.

&#x20;   error\_handling: Refuses if a required document cannot be loaded or parsed.



&#x20; - name: answer\_question

&#x20;   description: Searches the indexed documents and returns a single-source answer with citation or the exact refusal template.

&#x20;   input: User question and structured policy index.

&#x20;   output: Single-source answer with document and section citation, or refusal template.

&#x20;   error\_handling: Refuses when evidence is absent, ambiguous, or would require multiple documents.

