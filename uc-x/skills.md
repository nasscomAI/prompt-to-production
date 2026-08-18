skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads the three supplied policy documents and indexes their numbered sections by document name and section number.

&#x20;   input: Three policy document file paths in text format.

&#x20;   output: Indexed policy sections grouped by document name and section number.

&#x20;   error\_handling: Reports a clear error if a required document is missing or cannot be read.



&#x20; - name: answer\_question

&#x20;   description: Searches the indexed policy sections and returns a single-source answer with document and section citations or the exact refusal template.

&#x20;   input: A policy question as plain text.

&#x20;   output: An answer supported by exactly one source document with section citations, or the required refusal template.

&#x20;   error\_handling: Uses the exact refusal template when the question is not covered or cannot be answered from a single document.

